from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import json
import os
import tensorflow as tf
import numpy as np
from werkzeug import wrappers
from functools import reduce
import pprint

from tensorboard.backend import http_util
from tensorboard.backend.event_processing import event_multiplexer
from tensorboard.plugins import base_plugin
from tensorboard.backend.event_processing import io_wrapper


class ParamPlotPlugin(base_plugin.TBPlugin):
    """A plugin that serves greetings recorded during model runs."""

    # This static property will also be included within routes (URL paths)
    # offered by this plugin. This property must uniquely identify this plugin
    # from all other plugins.
    plugin_name = 'paramplot'
    MOST_RECENT = 'Most-Recent'
    MIN = 'Min'
    MAX = 'Max'
    AVERAGE = 'Average'

    def __init__(self, context):
        """Instantiates a ParamPlotPlugin.

        Args:
          context: A base_plugin.TBContext instance. A magic container that
            TensorBoard uses to make objects available to the plugin.
        """
        # We retrieve the multiplexer from the context and store a reference
        # to it.
        self._multiplexer = context.multiplexer
        self._context = context

        self._parameter_config = {}
        self.parameters = []
        self.printer = pprint.PrettyPrinter(indent=4)

    def _compute_config(self):
        # Read in all the config files in each run and create the combined config
        for run_name in self._multiplexer.Runs().keys():
            run_path = os.path.join(
                self._context.logdir, run_name, 'runparams.json')
            if os.path.exists(run_path):
                with open(run_path, 'r') as config_file_handle:
                    self._parameter_config[run_name] = json.loads(config_file_handle.read())

        # backfill any parameters which are missing with default values
        parameter_keys = list(
            map(lambda x: x.keys(), self._parameter_config.values()))
        self.parameters = set()
        for parameter_list in parameter_keys:
            self.parameters.update(parameter_list)

        for run_name in self._parameter_config:
            for parameter in self.parameters:
                if parameter not in self._parameter_config[run_name]:
                    # We assume all parameter values are numerical so nan is a suitable sentinel value
                    self._parameter_config[run_name][parameter] = np.nan

    def _get_valid_runs(self):
        return [run for run in self._multiplexer.Runs() if run in self._parameter_config]

    @wrappers.Request.application
    def tags_route(self, request):
        """A route (HTTP handler) that returns a response with tags.

        Returns:
          A response that contains a JSON object. The keys of the object
          are all the runs. Each run is mapped to a (potentially empty)
          list of all tags that are relevant to this plugin.
        """
        # This is a dictionary mapping from run to (tag to string content).
        # To be clear, the values of the dictionary are dictionaries.
        all_runs = self._multiplexer.PluginRunToTagToContent('scalars')

        # tagToContent is itself a dictionary mapping tag name to string
        # content. We retrieve the keys of that dictionary to obtain a
        # list of tags associated with each run.
        response = {
            run: list(tagToContent.keys())
            for (run, tagToContent) in all_runs.items()
        }

        return http_util.Respond(request, response, 'application/json')

    def get_plugin_apps(self):
        """Gets all routes offered by the plugin.

        This method is called by TensorBoard when retrieving all the
        routes offered by the plugin.

        Returns:
          A dictionary mapping URL path to route that handles it.
        """
        # Note that the methods handling routes are decorated with
        # @wrappers.Request.application.
        return {
            '/tags': self.tags_route,
            '/paramdatabytag': self._paramdatabytag_route,
            '/parameters': self._parameters_route,
            '/seriesnames': self._seriesnames_route,
        }

    def is_active(self):
        """Determines whether this plugin is active.

        This plugin is only active if there are runs in the runparams file which intersect with the available runs being monitored in the logdir

        Returns:
          Whether this plugin is active.
        """
        if not self._multiplexer:
            return False

        # The plugin is active if there are any runs in the runparam dictionary which are in the logdir
        return bool(any(self._get_valid_runs()))

    def aggregate_tensor_events(self, tensor_events, aggregation):
        event_list = [tf.make_ndarray(event.tensor_proto).item() for event in tensor_events]
        events_ndarray = np.array(event_list)
        
        if aggregation == ParamPlotPlugin.MIN:
            return np.amin(events_ndarray)
        elif aggregation == ParamPlotPlugin.MAX:
            return np.amax(events_ndarray)
        elif aggregation == ParamPlotPlugin.AVERAGE:
            return np.mean(events_ndarray)
        else:
            # Default to the most recent value semantics
            event_result = max(tensor_events, key=(lambda ev: ev.wall_time))
            return tf.make_ndarray(event_result.tensor_proto).item()

    def _param_keys(self, parameter):
        excluded_parameters = [param for param in self.parameters if not (parameter == param)]

        def run_to_paramkey(r):
            param_key = ""
            for p in excluded_parameters:
                param_key = param_key+("["+p+"-"+str(self._parameter_config[r][p])+"]")
        
        return {run: run_to_paramkey(run) for run in self._get_valid_runs()}

    def _get_tensor_events_payload(self, parameter, tag, aggregation, seriesKey):
        processed_events = {}
        excluded_parameters = [param for param in self.parameters if not (parameter == param or parameter == seriesKey)]

        # Loop through all the runs and compute the data which has parameter value as the independent variable and tensors as the dependent value
        for run in self._get_valid_runs():
            tensor_events = self._multiplexer.Tensors(run, tag)
            param_value = self._parameter_config[run][parameter]
            series_key_value = self._parameter_config[run][seriesKey]

            if not np.isnan(series_key_value):
                # We want to return a dictionary which has a key for each series where the other parameters remain equal
                param_key = "["+seriesKey+": "+str(series_key_value)+"]"

                # Create a two level dictionary for the series key with a sub key as the parameter value (we will then aggregate over this so each seriesKey defines a series)
                if param_key in processed_events:
                    if param_value in processed_events[param_key]:
                        processed_events[param_key][param_value].append(self.aggregate_tensor_events(tensor_events, aggregation))
                    else:
                        processed_events[param_key][param_value] = [self.aggregate_tensor_events(tensor_events, aggregation)]
                else:
                    processed_events[param_key] = {param_value: [self.aggregate_tensor_events(tensor_events, aggregation)]}
        
        result = {}
        # Aggregate the points so that there are only series which are keyed by the provided parameter name (seriesKey)
        for param_key in processed_events:
            result[param_key] = []
            for param_value in processed_events[param_key]:
                result[param_key].append((param_value, np.nanmean(np.array(processed_events[param_key][param_value]))))

        return result

    @wrappers.Request.application
    def _paramdatabytag_route(self, request):
        """A route which returns the runparams for a particular run along with the tag specific data

        Returns:
          A JSON object of the form:
          [(wall_time, parameter_value, tag)] for each run
        """

        parameter = request.args.get('parameter')
        tag = request.args.get('tag')
        aggregation = request.args.get('aggregation')
        seriesKey = request.args.get('serieskey')

        self._multiplexer.Reload()

        response = self._get_tensor_events_payload(parameter, tag, aggregation, seriesKey)
        return http_util.Respond(request, response, 'application/json')

    @wrappers.Request.application
    def _parameters_route(self, request):
        """A route which returns the list of paramaters which each run is tagged with in the run parameters json file

        Returns: A JSON object which is an array of parameter names (it is an assumption of the runparams schema all 
        runs will be tagged with the same parameters)
        """
        self._compute_config()

        response = {
            "payload": list(self.parameters)
        }
        return http_util.Respond(request, response, 'application/json')
    
    @wrappers.Request.application
    def _seriesnames_route(self, request):
        """A route which returns the dictionary of series names when given a parameter (these will be used to index each series in a plot)

        Returns: A JSON object of the form {"run1": "[parameter-value]...", ... }
        """

        parameter = request.args.get('parameter')
        parameter_keys = self._param_keys(parameter)

        return http_util.Respond(request, parameter_keys, 'application/json')
