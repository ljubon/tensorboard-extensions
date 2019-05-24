from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import os
import json
import pprint
import re

import queue
import threading

from werkzeug import wrappers
from collections import deque

from tensorboard.backend import http_util
from tensorboard.plugins import base_plugin
from tensorboard.backend.event_processing import io_wrapper
from tensorboard.backend.event_processing import plugin_event_accumulator as event_accumulator

from .runsenabler_profiler import RunsEnablerLogger, RunsEnablerProfiler, NoOpLogger, NoOpProfiler


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
        self._accumulator_cache = {}
        self._context = context
        self.logdir = context.logdir
        self.printer = pprint.PrettyPrinter(indent=4)
        self.enabler_threads = context.flags.runsenabler_threads

        # Load the multiplexer with runs for the first time so that we can reload the accumulators on every added run 
        # and register all the plugins with gr tensorboard
        self._multiplexer.Reload()
        # self.runs = self._get_runs()

        # Create the runsenabler log file which contains profiling times for all the methods
        self.logger = RunsEnablerLogger() if context.flags.enable_profiling else NoOpLogger()
        self.profiler = RunsEnablerProfiler(self.logger) if context.flags.enable_profiling else NoOpProfiler()

    def get_plugin_apps(self):
        """Gets all routes offered by the plugin.
        """
        # Note that the methods handling routes are decorated with
        # @wrappers.Request.application.
        return {
            '/enablerun': self.enablerun_route,
            '/disablerun': self.disablerun_route,
            '/runs': self.runstate_route,
            '/enableall': self.enableall_route,
            '/disableall': self.disableall_route,
            '/disablenonmatching': self.disablenonmatching_route,
        }

    def is_active(self):
        """Determines whether this plugin is active.

        This plugin is only active if there are runs in the runparams config dictionary which intersect the available runs being monitored in the logdir

        Returns:
        Whether this plugin is active.
        """

        return True
    
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
        return http_util.Respond(request, {}, 'application/json')
    
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
        return http_util.Respond(request, {}, 'application/json')

    def _get_runs(self):
        return list(map(lambda x: os.path.relpath(x, self.logdir), io_wrapper.GetLogdirSubdirectories(self.logdir)))

    def _get_runstate(self, enable_new_runs=False):
        # This assumes that the run names are entirely described by those sub directories which contains events files (1 per directory)
        run_path_names = self._get_runs()
        
        # Determine the set of runs which have been newly added (i.e. in the new run set but not the old)
        old_run_set = set(self.runs)
        new_run_set = set(run_path_names)
        newly_added_runs = new_run_set.difference(old_run_set)
        
        # Update the runs which are currently being 
        new_run_state = {run: (run in self._multiplexer._accumulators or (enable_new_runs and run in newly_added_runs)) for run in run_path_names}
        self.runs = run_path_names
        
        return new_run_state, newly_added_runs
        
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
        enable_new_runs = request.args.get('enableNewRuns')

        self.logger.log_message_info("executing runstate_route (/runs)")
        with self.profiler.ProfileBlock():
            with self.profiler.TimeBlock("_get_runstate()"):
                # Handles the case where new runs are added after tensorboard has begun 
                self.run_state, new_runs = self._get_runstate(enable_new_runs)
                # If there are new runs and the user has specified to enable all new runs, then we will have these in the run state so create accumulators for these
                # and reload the multiplexer to delete the runs whose directories have been removed and to create the runs whose directories have just added
                if enable_new_runs and len(new_runs) > 0:
                    self._add_runs(new_runs)
            with self.profiler.TimeBlock("_multiplexer.Reload()"):
                self._multiplexer.Reload()

        # Update the runs with any new runs in the original logdir and remove any which have been deleted
        return http_util.Respond(request, self.run_state, 'application/json')
    
    def _remove_runs_by_regex(self, regex):
        with self._multiplexer._accumulators_mutex:
            runs = [r for r in self._get_runs() if r in self._multiplexer._accumulators and re.search(regex, r)]
            with self.profiler.TimeBlock("removing all the runs which match the regex"):
                for run in runs:
                    with self.profiler.TimeBlock(run):
                        if run in self._multiplexer._accumulators:
                            del self._multiplexer._accumulators[run]
                        if run in self._multiplexer._paths:
                            del self._multiplexer._paths[run]

    def _add_runs(self, runs):
        # create an items queue containing runs which will be accessed by multiple threads
        items_queue = queue.Queue()
        for run in runs:
            items_queue.put(run)

        def Worker():
            """Keeps reloading accumulators til none are left."""
            while True:
                try:
                    run = items_queue.get(block=False)
                except queue.Empty:
                    # No more runs to reload.
                    break
                try:
                    self._multiplexer._accumulators[run] = event_accumulator.EventAccumulator(
                        os.path.join(self.logdir, run),
                        size_guidance=self._multiplexer._size_guidance,
                        tensor_size_guidance=self._multiplexer._tensor_size_guidance,
                        purge_orphaned_data=self._multiplexer.purge_orphaned_data)
                    self._multiplexer._paths[run] = os.path.join(self.logdir, run)
                finally:
                    items_queue.task_done()
        
        if self.enabler_threads > 1:
            num_threads = min(self.enabler_threads, len(runs))
            for i in range(num_threads):
                thread = threading.Thread(target=Worker, name='Accumulator Creator %d' % i)
                thread.daemon = True
                thread.start()
            items_queue.join()
        else:
            Worker()


    def _add_runs_by_regex(self, regex):
            runs = [r for r in self._get_runs() if re.search(regex, r)]
            self.logger.log_message_info("number of runs to load: " + str(len(runs)))
            with self.profiler.TimeBlock("adding all the runs which match the regex"):
                self._add_runs(runs)
        
    def _remove_runs_not_matching_regex(self, regex):
        with self._multiplexer._accumulators_mutex:
            runs = [r for r in self._get_runs() if r in self._multiplexer._accumulators and not re.search(regex, r)]
            with self.profiler.TimeBlock("removing all the runs which do not match the regex"):
                for run in runs:
                    with self.profiler.TimeBlock(run):
                        if run in self._multiplexer._accumulators:
                            del self._multiplexer._accumulators[run]
                        if run in self._multiplexer._paths:
                            del self._multiplexer._paths[run]
            
    def _format_regex(self, regex):
        regex = regex[1:-1]
        regex = regex if regex != "(:?)" else ".*"
        return re.compile(regex)
     
    @wrappers.Request.application
    def enableall_route(self, request):
        regex = self._format_regex(request.args.get('regex'))
        
        self.logger.log_message_info("executing enableall_route (/enableall)")
        with self.profiler.ProfileBlock():
            self._add_runs_by_regex(regex)

        return http_util.Respond(request, {}, 'application/json')
    
    @wrappers.Request.application
    def disableall_route(self, request):
        regex = self._format_regex(request.args.get('regex'))

        self.logger.log_message_info("executing disableall_route (/disableall)")
        with self.profiler.ProfileBlock():
            self._remove_runs_by_regex(regex)
        
        return http_util.Respond(request, {}, 'application/json')
    
    @wrappers.Request.application
    def disablenonmatching_route(self, request):
        regex = self._format_regex(request.args.get('regex'))
        
        self.logger.log_message_info("executing disableallnonmatching_route (/disableallnonmatching)")
        with self.profiler.ProfileBlock():
            self._remove_runs_not_matching_regex(regex)
        
        return http_util.Respond(request, {}, 'application/json')
