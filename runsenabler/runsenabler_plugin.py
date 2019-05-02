from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import os
import sys
from subprocess import call
import shutil
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
    MIN_DEFAULT = 10

    def __init__(self, context, actual_logir):
        """Instantiates a RunsEnablerPlugin.

        Args:
        context: A base_plugin.TBContext instance. A magic container that
            TensorBoard uses to make objects available to the plugin.
        """
        # We retrieve the multiplexer from the context and store a reference
        # to it.
        self._multiplexer = context.multiplexer
        self._context = context
        self.actual_logdir = actual_logir
        self.temp_logdir = context.logdir
        self.enabled = context.flags.enable_runsenabler
        
        if self.enabled:
            # Get all the runs in the original logdirectory and set them to false by default
            sortedRuns = self._get_runs_from_actual_logdir()
            self._run_state = {run: False for run in sortedRuns}

            # move the most recent files to the temp dir via a symlink - ensures that at least one run (likely the most relevant run) will be enabled
            num_files = min(RunsEnablerPlugin.MIN_DEFAULT, len(sortedRuns))
            for run in sortedRuns[-num_files:]:
                run_name = run.replace(self.actual_logdir+os.path.sep, "")
                runpath = self._create_symlink_for_run(run_name)
                self._enable_run(runpath, run_name)
    
    def _get_runs_from_actual_logdir(self):
        dir_list = sorted(list(io_wrapper.GetLogdirSubdirectories(self.actual_logdir)), key=os.path.getmtime)
        return [run.replace(self.actual_logdir+os.path.sep, "") for run in dir_list]


    def get_plugin_apps(self):
        """Gets all routes offered by the plugin.
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

        This plugin is only active if there are runs in the runparams config dictionary which intersect the available runs being monitored in the logdir

        Returns:
        Whether this plugin is active.
        """

        return self.enabled
    
    def _create_symlink_for_run(self, run):
        # Create symlink from run in LOGDIR to TEMPDIR
        src_path = os.path.join(self.actual_logdir, run)
        dest_path = os.path.join(self.temp_logdir, run)
        dest_dir = os.path.dirname(dest_path)
        
        # Create the directories of the destination symlink first
        if not os.path.exists(dest_dir):
            os.makedirs(dest_dir)
        
        if sys.platform in ['win32', 'cygwin']:
            # Windows doesn't interact well with os.symlink due to the SECreateSymbolicLink privilege not being granted to non-admin users
            # create an ntfs junction instead
            call(['mklink', '/j', dest_path, src_path], shell=True)
        else:
            # Other operating systems are fine
            os.symlink(src_path, dest_path)
            

        return dest_path

    def _enable_run(self, runpath, run):
        # Call reload on the multiplexer (required so that the newly added run will be loaded as well)
        self._multiplexer.Reload()

        # Add the run to the multiplexer (this will automatically reload the accumulators)
        self._multiplexer.AddRun(runpath, run)
        self._run_state[run] = True

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

        runpath = self._create_symlink_for_run(run)
        self._enable_run(runpath, run)

        return http_util.Respond(request, self._run_state, 'application/json')

    def _delete_symlink_for_run(self, run):
        # Delete symlink from run in LOGDIR to TEMPDIR
        dest_path = os.path.join(self.temp_logdir, run)

        if os.path.islink(dest_path):
            os.unlink(dest_path)
        else:
            # We assume that the link is a junction created for windows so we just need to remove the directory
            os.rmdir(dest_path)

    
    def _disable_run(self, run):
        # Call reload on the multiplexer, this will detect that the directory no longer exists and delete the accumulator
        self._multiplexer.Reload()
        self._run_state[run] = False

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
        self._delete_symlink_for_run(run)
        self._disable_run(run)

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
                           for run in self._get_runs_from_actual_logdir()}
        return http_util.Respond(request, self._run_state, 'application/json')
