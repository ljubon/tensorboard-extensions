from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import os
import json
import tensorflow as tf
from werkzeug import wrappers

from tensorboard.backend import http_util
from tensorboard.backend.event_processing import event_multiplexer
from tensorboard.plugins import base_plugin
from tensorboard.backend.event_processing import io_wrapper


class RunsEnablerPlugin(base_plugin.TBPlugin):
    """A plugin that controls which runs tensorboard can inspect"""

    # This static property will also be included within routes (URL paths)
    # offered by this plugin. This property must uniquely identify this plugin
    # from all other plugins.
    plugin_name = 'runsenabler'

    def __init__(self, context: base_plugin.TBContext, actual_logir: str):
        """Instantiates a RunsEnablerPlugin.

        Args:
        context: A base_plugin.TBContext instance. A magic container that
            TensorBoard uses to make objects available to the plugin.
        """
        # We retrieve the multiplexer from the context and store a reference
        # to it.
        self._multiplexer: event_multiplexer.EventMultiplexer = context.multiplexer
        self._context = context
        self.actual_logdir = actual_logir
        self.temp_logdir = context.logdir

        # Get all the runs in the original logdirectory and set them to false by default
        self._run_state = {
            run: False for run in io_wrapper.GetLogdirSubdirectories(self.actual_logdir)}

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
            '/enablerun': self.enablerun_route,
            '/disablerun': self.disablerun_route,
            '/runs': self.runstate_route,
        }

    def is_active(self):
        """Determines whether this plugin is active.

        This plugin is only active if there are runs in the runparams file which intersect with the available runs being monitored in the logdir

        Returns:
        Whether this plugin is active.
        """

        # The plugin is always active (will have to handle the case where )
        return True

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

        # Create symlink from run in LOGDIR to TEMPDIR
        src_path = os.path.join(self.actual_logdir, run)
        dest_path = os.path.join(self.temp_logdir, run)
        os.symlink(src_path, dest_path)

        # Call reload on the multiplexer (required so that the newly added run will be loaded as well)
        self._multiplexer.Reload()

        # Add the run to the multiplexer (this will automatically reload the accumulators)
        self._multiplexer.AddRun(run)
        self._run_state[src_path] = True

        return http_util.Respond(request, self._run_state, 'application/json')

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

        # Delete symlink from run in LOGDIR to TEMPDIR
        src_path = os.path.join(self.actual_logdir, run)
        dest_path = os.path.join(self.temp_logdir, run)
        os.rmdir(dest_path)

        # Call reload on the multiplexer, this will detect that the directory no longer exists and delete the accumulator
        self._multiplexer.Reload()
        self._run_state[src_path] = False

        return http_util.Respond(request, self._run_state, 'application/json')

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
        # Update the runs with any new runs in the original logdir and remove any which have been deleted
        self._run_state = {run: (self._run_state[run] if run in self._run_state else False)
                           for run in io_wrapper.GetLogdirSubdirectories(self.actual_logdir)}
        return http_util.Respond(request, self._run_state, 'application/json')
