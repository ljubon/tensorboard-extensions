from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import os
import json
import pprint
from werkzeug import wrappers

from tensorboard.backend import http_util
from tensorboard.plugins import base_plugin
from tensorboard.backend.event_processing import io_wrapper


class RunsEnablerPlugin(base_plugin.TBPlugin):
    """A plugin that controls which runs tensorboard can inspect"""

    # This static property will also be included within routes (URL paths)
    # offered by this plugin. This property must uniquely identify this plugin
    # from all other plugins.
    plugin_name = 'runsenabler'
    MIN_DEFAULT = 10

    def __init__(self, context):
        """Instantiates a RunsEnablerPlugin.

        Args:
        context: A base_plugin.TBContext instance. A magic container that
            TensorBoard uses to make objects available to the plugin.
        """
        # We retrieve the multiplexer from the context and store a reference
        # to it.
        self._multiplexer = context.multiplexer
        self._accumulators = context.multiplexer._accumulators
        self._accumulators_mutex = context.multiplexer._accumulators_mutex
        self._context = context
        self.logdir = context.logdir
        self.enabled = context.flags.enable_runsenabler
        self.printer = pprint.PrettyPrinter(indent=4)

        # Load the multiplexer with runs for the first time so that we can reload the accumulators on every added run 
        # and register all the plugins with gr tensorboard
        self._multiplexer.Reload()

    def get_plugin_apps(self):
        """Gets all routes offered by the plugin.
        """
        # Note that the methods handling routes are decorated with
        # @wrappers.Request.application.
        return {
            '/enablerun': self.enablerun_route,
            '/disablerun': self.disablerun_route,
            '/runs': self.runstate_route,
            '/updaterunstate': self.updaterunstate_route,
        }

    def is_active(self):
        """Determines whether this plugin is active.

        This plugin is only active if there are runs in the runparams config dictionary which intersect the available runs being monitored in the logdir

        Returns:
        Whether this plugin is active.
        """

        return self.enabled
    
    def _enable_run(self, run):
        run_path = os.path.join(self.logdir, run)
        self._multiplexer.AddRun(run_path, run)

    @wrappers.Request.application
    def enablerun_route(self, request):
        """Route to enable the run which has been provided by the request
        e.g. using os.symlink to create the link

        Returns:
        A JSON serialisation of the run directory state of the form:
        {
            "run1": True,
            "run2": True,
            "run3": False,
            ...
        }
        """
        run = request.args.get('run')
        self._enable_run(run)
        return http_util.Respond(request, self._get_runstate(), 'application/json')
    
    def _disable_run(self, run):
        with self._multiplexer._accumulators_mutex:
            if run in self._multiplexer._accumulators:
                del self._multiplexer._accumulators[run]

    @wrappers.Request.application
    def disablerun_route(self, request):
        """Route to disable the run which has been provided by the request
        e.g. using os.rmdir to remove the symlink which will be a directory (does not remove the contents of the directory)

        Returns:
        A JSON serialisation of the run directory state of the form:
        {
            "run1": True,
            "run2": True,
            "run3": False,
            ...
        }
        """
        run = request.args.get('run')
        self._disable_run(run)
        return http_util.Respond(request, self._get_runstate(), 'application/json')

    def _get_runstate(self):
        # This assumes that the run names are entirely described by those sub directories which contains events files (1 per directory)
        run_path_names = list(map(lambda x: os.path.relpath(x, self.logdir), io_wrapper.GetLogdirSubdirectories(self.logdir)))
        return {run: (run in self._multiplexer._accumulators) for run in run_path_names}

    @wrappers.Request.application
    def runstate_route(self, request):
        """Route to return the run state (dictionary mapping run names to whether they enabled)

        Returns:
        A JSON serialisation of the run directory state of the form:
        {
            "run1": True,
            "run2": True,
            "run3": False,
            ...
        }
        """
        run_state = self._get_runstate()
        # Update the runs with any new runs in the original logdir and remove any which have been deleted
        return http_util.Respond(request, run_state, 'application/json')
    
    def _remove_runs(self, runs):
        with self._multiplexer._accumulators_mutex:
            for run in runs:
                if run in self._multiplexer._accumulators:
                    del self._multiplexer._accumulators[run]

    def _add_runs(self, runs):
        for run in runs:
            run_path = os.path.join(self.logdir, run)
            self._multiplexer.AddRun(run_path, run)

    @wrappers.Request.application
    def updaterunstate_route(self, request):
        run_state = json.loads(request.args.get('runState'))
        
        run_state_before = self._get_runstate()

        runs_to_enable = []
        runs_to_disable = []

        # Determine from the new state whether we need to enable or disable any states
        for run in run_state:
            if run_state[run] and not run_state_before[run]:
                # The run was enabled when it was disabled before
                runs_to_enable.append(run)
            elif not run_state[run] and run_state_before[run]:
                # The run was disabled when it was enabled before
                runs_to_disable.append(run)

        # Delete the disabled runs and create the enabled ones
        self._remove_runs(runs_to_disable)
        self._add_runs(runs_to_enable)

        new_run_state = self._get_runstate()
        return http_util.Respond(request, new_run_state, 'application/json')
