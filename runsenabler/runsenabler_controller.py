from tensorboard.backend.event_processing import plugin_event_accumulator as event_accumulator
import os
import shutil
import pathlib

class RunsController:
    def enable_run(self, run):
        raise NotImplementedError
    def disable_run(self, run):
        raise NotImplementedError
    def enable_runs(self, runs):
        raise NotImplementedError
    def disable_runs(self, runs):
        raise NotImplementedError

class EventMultiplexerRunsController(RunsController):
    def __init__(self, multiplexer, logdir):
        super(EventMultiplexerRunsController, self).__init__()
        self._multiplexer = multiplexer
        self.logdir = logdir

    def enable_run(self, run):
        run_path = os.path.join(self.logdir, run)
        self._multiplexer.AddRun(run_path, run)
    
    def disable_run(self, run):
        with self._multiplexer._accumulators_mutex:
            if run in self._multiplexer._accumulators:
                del self._multiplexer._accumulators[run]
    
    def enable_runs(self, runs):
        for run in runs:
            self._multiplexer._accumulators[run] = event_accumulator.EventAccumulator(
                os.path.join(self.logdir, run),
                size_guidance=self._multiplexer._size_guidance,
                tensor_size_guidance=self._multiplexer._tensor_size_guidance,
                purge_orphaned_data=self._multiplexer.purge_orphaned_data)
            self._multiplexer._paths[run] = os.path.join(self.logdir, run)
    
    def disable_runs(self, runs):
        for run in runs:
            if run in self._multiplexer._accumulators:
                del self._multiplexer._accumulators[run]
            if run in self._multiplexer._paths:
                del self._multiplexer._paths[run]

class FilesystemRunsController(RunsController):
    def __init__(self, actual_logdir, base_controller):
        super(FilesystemRunsController, self).__init__()
        # This would have been set on startup to be the new logdir
        self.temp_logdir = pathlib.Path(base_controller.logdir)
        self.logdir = pathlib.Path(actual_logdir)
        self.base_controller = base_controller

    def _enable_run(self, run):
        # copy the events file and run directory from the logdir to the temp dir
        old_run_path = self.logdir / run
        new_run_path = self.temp_logdir / run
        print("making run directory: " + str(new_run_path))
        new_run_path.mkdir(parents=True)
        for events_file in old_run_path.glob("events.out.tfevents.*"):
            shutil.copy(str(events_file), str(new_run_path))
        for metadata_file in old_run_path.glob("*.json"):
            shutil.copy(str(metadata_file), str(new_run_path))

    def enable_run(self, run):
        self.base_controller.enable_run(run)
        self._enable_run(run)
    
    def _disable_run(self, run):
        run_path = self.temp_logdir / run
        shutil.rmtree(str(run_path))

    def disable_run(self, run):
        self.base_controller.disable_run(run)
        self._disable_run(run)
    
    def enable_runs(self, runs):
        self.base_controller.enable_runs(runs)
        for run in runs:
            self._enable_run(run)
    
    def disable_runs(self, runs):
        self.base_controller.disable_runs(runs)
        for run in runs:
            self._disable_run(run)