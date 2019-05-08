from tensorboard.backend.event_processing import event_multiplexer
from tensorboard.backend.event_processing import directory_watcher
from tensorboard.backend.event_processing import event_accumulator
from tensorboard.backend.event_processing import io_wrapper

from .logging import get_logger

import os
import threading

import six

logger = get_logger()

class EventRunsController(object):
    """An EventRunsController functions as a Tensorboard EventMultiplexer would, such as managing all the accumulators for each run 
    But also allows for the deletion of accumulators via some simple methods rather than just having this in the reload logic

    The code for adding runs and the plugin related logic is identical to tensorboard
    """
    def __init__(self, size_guidance=None, purge_orphaned_data=True, logdir=None, preload_most_recent_runs=50):
        logger.info('Event Runs Controller initializing.')
        self._accumulators_mutex = threading.Lock()
        self._accumulators = {}
        self._paths = {}
        self._conflicting_name_counter = {}
        self._reload_called = False
        self._size_guidance = (size_guidance or event_accumulator.DEFAULT_SIZE_GUIDANCE)
        self.purge_orphaned_data = purge_orphaned_data
        self.logdir = logdir
        
        # Preload the N most recent runs (defaults to 10)
        if logdir is not None:
            run_path_map = self._getRunPathMapFromLogdir(logdir, preload_most_recent_runs)

        if run_path_map is not None:
            logger.info('Event Multiplexer doing initialization load for %s', run_path_map)
            for (run, path) in six.iteritems(run_path_map):
                self.AddRun(path, run)
        logger.info('Event Multiplexer done initializing')
    
    def _getRunPathMapFromLogdir(self, logdir, most_recent_num):
        dir_list = sorted(list(io_wrapper.GetLogdirSubdirectories(logdir)), key=os.path.getmtime)
        num_files = min(most_recent_num, len(dir_list))
        return {path.replace(logdir+os.path.sep, ""): path for path in dir_list[-num_files:]}
    
    def AddRun(self, path, name=None):
        """Add a run to the multiplexer.
        If the name is not specified, it is the same as the path.
        If a run by that name exists, and we are already watching the right path,
        do nothing. If we are watching a different path, replace the event
        accumulator.
        If `Reload` has been called, it will `Reload` the newly created
        accumulators.
        Args:
        path: Path to the event files (or event directory) for given run.
        name: Name of the run to add. If not provided, is set to path.
        Returns:
        The `EventMultiplexer`.
        """
        name = name or path
        accumulator = None
        with self._accumulators_mutex:
            if name not in self._accumulators or self._paths[name] != path:
                if name in self._paths and self._paths[name] != path:
                    logger.warn('Conflict for name %s: old path %s, new path %s',
                                        name, self._paths[name], path)
                logger.info('Constructing EventAccumulator for %s', path)
                accumulator = event_accumulator.EventAccumulator(
                    path,
                    size_guidance=self._size_guidance,
                    purge_orphaned_data=self.purge_orphaned_data)
                self._accumulators[name] = accumulator
                self._paths[name] = path
        if accumulator:
            if self._reload_called:
                accumulator.Reload()
        return self
    
    def AddRunsFromDirectory(self, path, name=None):
        """Load runs from a directory; recursively walks subdirectories.
        If path doesn't exist, no-op. This ensures that it is safe to call
        `AddRunsFromDirectory` multiple times, even before the directory is made.
        If path is a directory, load event files in the directory (if any exist) and
        recursively call AddRunsFromDirectory on any subdirectories. This mean you
        can call AddRunsFromDirectory at the root of a tree of event logs and
        TensorBoard will load them all.
        If the `EventMultiplexer` is already loaded this will cause
        the newly created accumulators to `Reload()`.
        Args:
        path: A string path to a directory to load runs from.
        name: Optionally, what name to apply to the runs. If name is provided
            and the directory contains run subdirectories, the name of each subrun
            is the concatenation of the parent name and the subdirectory name. If
            name is provided and the directory contains event files, then a run
            is added called "name" and with the events from the path.
        Raises:
        ValueError: If the path exists and isn't a directory.
        Returns:
        The `EventMultiplexer`.
        """
        logger.info('Starting AddRunsFromDirectory: %s', path)
        for subdir in io_wrapper.GetLogdirSubdirectories(path):
            logger.info('Adding events from directory %s', subdir)
            rpath = os.path.relpath(subdir, path)
            subname = os.path.join(name, rpath) if name else rpath
            self.AddRun(subdir, name=subname)
        logger.info('Done with AddRunsFromDirectory: %s', path)
        return self
    
    def RemoveRun(self, path, name=None):
      """
      Simple method to delete the acculmulator for a particular run
      """
      if name is not None:
        logger.warn("Deleting accumulator '%s'", name)
        with self._accumulators_mutex:
          self._accumulators[name] = None

    def GetRunState(self):
      """
      Returns a python dictionary which maps run names whether they have accumulators
      """
      logger.info('Getting the run state for logdir %s' % self.logdir)
      
      # This assumes that the run names are entirely described by those sub directories which contains events files (1 per directory)
      run_path_names = list(map(lambda x: os.path.relpath(x, self.logdir), io_wrapper.GetLogdirSubdirectories(self.logdir)))
      run_state = {run: (run in self._accumulators and self._accumulators[run] is not None) for run in run_path_names}

      return run_state
    
    def Reload(self):
      """Call `Reload` on every `EventAccumulator`."""
      logger.info('Beginning EventMultiplexer.Reload()')
      self._reload_called = True
      # Build a list so we're safe even if the list of accumulators is modified
      # even while we're reloading.
      with self._accumulators_mutex:
        items = list(self._accumulators.items())

      names_to_delete = set()
      for name, accumulator in items:
        try:
          if accumulator is not None:
            accumulator.Reload()
        except (OSError, IOError) as e:
          logger.error("Unable to reload accumulator '%s': %s", name, e)
        except directory_watcher.DirectoryDeletedError:
          names_to_delete.add(name)

      with self._accumulators_mutex:
        for name in names_to_delete:
          logger.warn("Deleting accumulator '%s'", name)
          self._accumulators[name] = None
      logger.info('Finished with EventMultiplexer.Reload()')
      return self
    
    def PluginAssets(self, plugin_name):
      """Get index of runs and assets for a given plugin.
      Args:
        plugin_name: Name of the plugin we are checking for.
      Returns:
        A dictionary that maps from run_name to a list of plugin
          assets for that run.
      """
      with self._accumulators_mutex:
        # To avoid nested locks, we construct a copy of the run-accumulator map
        items = list(six.iteritems(self._accumulators))

      return {run: accum.PluginAssets(plugin_name) for run, accum in items if accum is not None}

    def RetrievePluginAsset(self, run, plugin_name, asset_name):
      """Return the contents for a specific plugin asset from a run.
      Args:
        run: The string name of the run.
        plugin_name: The string name of a plugin.
        asset_name: The string name of an asset.
      Returns:
        The string contents of the plugin asset.
      Raises:
        KeyError: If the asset is not available.
      """
      accumulator = self.GetAccumulator(run)
      return accumulator.RetrievePluginAsset(plugin_name, asset_name)

    def FirstEventTimestamp(self, run):
      """Return the timestamp of the first event of the given run.
      This may perform I/O if no events have been loaded yet for the run.
      Args:
        run: A string name of the run for which the timestamp is retrieved.
      Returns:
        The wall_time of the first event of the run, which will typically be
        seconds since the epoch.
      Raises:
        KeyError: If the run is not found.
        ValueError: If the run has no events loaded and there are no events on
          disk to load.
      """
      accumulator = self.GetAccumulator(run)
      return accumulator.FirstEventTimestamp()

    def Scalars(self, run, tag):
      """Retrieve the scalar events associated with a run and tag.
      Args:
        run: A string name of the run for which values are retrieved.
        tag: A string name of the tag for which values are retrieved.
      Raises:
        KeyError: If the run is not found, or the tag is not available for
          the given run.
      Returns:
        An array of `event_accumulator.ScalarEvents`.
      """
      accumulator = self.GetAccumulator(run)
      return accumulator.Scalars(tag)

    def Graph(self, run):
      """Retrieve the graph associated with the provided run.
      Args:
        run: A string name of a run to load the graph for.
      Raises:
        KeyError: If the run is not found.
        ValueError: If the run does not have an associated graph.
      Returns:
        The `GraphDef` protobuf data structure.
      """
      accumulator = self.GetAccumulator(run)
      return accumulator.Graph()

    def MetaGraph(self, run):
      """Retrieve the metagraph associated with the provided run.
      Args:
        run: A string name of a run to load the graph for.
      Raises:
        KeyError: If the run is not found.
        ValueError: If the run does not have an associated graph.
      Returns:
        The `MetaGraphDef` protobuf data structure.
      """
      accumulator = self.GetAccumulator(run)
      return accumulator.MetaGraph()

    def RunMetadata(self, run, tag):
      """Get the session.run() metadata associated with a TensorFlow run and tag.
      Args:
        run: A string name of a TensorFlow run.
        tag: A string name of the tag associated with a particular session.run().
      Raises:
        KeyError: If the run is not found, or the tag is not available for the
          given run.
      Returns:
        The metadata in the form of `RunMetadata` protobuf data structure.
      """
      accumulator = self.GetAccumulator(run)
      return accumulator.RunMetadata(tag)

    def Histograms(self, run, tag):
      """Retrieve the histogram events associated with a run and tag.
      Args:
        run: A string name of the run for which values are retrieved.
        tag: A string name of the tag for which values are retrieved.
      Raises:
        KeyError: If the run is not found, or the tag is not available for
          the given run.
      Returns:
        An array of `event_accumulator.HistogramEvents`.
      """
      accumulator = self.GetAccumulator(run)
      return accumulator.Histograms(tag)

    def CompressedHistograms(self, run, tag):
      """Retrieve the compressed histogram events associated with a run and tag.
      Args:
        run: A string name of the run for which values are retrieved.
        tag: A string name of the tag for which values are retrieved.
      Raises:
        KeyError: If the run is not found, or the tag is not available for
          the given run.
      Returns:
        An array of `event_accumulator.CompressedHistogramEvents`.
      """
      accumulator = self.GetAccumulator(run)
      return accumulator.CompressedHistograms(tag)

    def Images(self, run, tag):
      """Retrieve the image events associated with a run and tag.
      Args:
        run: A string name of the run for which values are retrieved.
        tag: A string name of the tag for which values are retrieved.
      Raises:
        KeyError: If the run is not found, or the tag is not available for
          the given run.
      Returns:
        An array of `event_accumulator.ImageEvents`.
      """
      accumulator = self.GetAccumulator(run)
      return accumulator.Images(tag)

    def Audio(self, run, tag):
      """Retrieve the audio events associated with a run and tag.
      Args:
        run: A string name of the run for which values are retrieved.
        tag: A string name of the tag for which values are retrieved.
      Raises:
        KeyError: If the run is not found, or the tag is not available for
          the given run.
      Returns:
        An array of `event_accumulator.AudioEvents`.
      """
      accumulator = self.GetAccumulator(run)
      return accumulator.Audio(tag)

    def Tensors(self, run, tag):
      """Retrieve the tensor events associated with a run and tag.
      Args:
        run: A string name of the run for which values are retrieved.
        tag: A string name of the tag for which values are retrieved.
      Raises:
        KeyError: If the run is not found, or the tag is not available for
          the given run.
      Returns:
        An array of `event_accumulator.TensorEvent`s.
      """
      accumulator = self.GetAccumulator(run)
      return accumulator.Tensors(tag)

    def PluginRunToTagToContent(self, plugin_name):
      """Returns a 2-layer dictionary of the form {run: {tag: content}}.
      The `content` referred above is the content field of the PluginData proto
      for the specified plugin within a Summary.Value proto.
      Args:
        plugin_name: The name of the plugin for which to fetch content.
      Returns:
        A dictionary of the form {run: {tag: content}}.
      """
      mapping = {}
      for run in self.Runs():
        try:
          tag_to_content = self.GetAccumulator(run).PluginTagToContent(
              plugin_name)
        except KeyError:
          # This run lacks content for the plugin. Try the next run.
          continue
        mapping[run] = tag_to_content
      return mapping

    def SummaryMetadata(self, run, tag):
      """Return the summary metadata for the given tag on the given run.
      Args:
        run: A string name of the run for which summary metadata is to be
          retrieved.
        tag: A string name of the tag whose summary metadata is to be
          retrieved.
      Raises:
        KeyError: If the run is not found, or the tag is not available for
          the given run.
      Returns:
        A `SummaryMetadata` protobuf.
      """
      accumulator = self.GetAccumulator(run)
      return accumulator.SummaryMetadata(tag)

    def Runs(self):
      """Return all the run names in the `EventMultiplexer`.
      Returns:
      ```
        {runName: { images: [tag1, tag2, tag3],
                    scalarValues: [tagA, tagB, tagC],
                    histograms: [tagX, tagY, tagZ],
                    compressedHistograms: [tagX, tagY, tagZ],
                    graph: true, meta_graph: true}}
      ```
      """
      with self._accumulators_mutex:
        # To avoid nested locks, we construct a copy of the run-accumulator map
        items = list(six.iteritems(self._accumulators))
      return {run_name: accumulator.Tags() for run_name, accumulator in items}

    def RunPaths(self):
      """Returns a dict mapping run names to event file paths."""
      return self._paths

    def GetAccumulator(self, run):
      """Returns EventAccumulator for a given run.
      Args:
        run: String name of run.
      Returns:
        An EventAccumulator object.
      Raises:
        KeyError: If run does not exist.
      """
      with self._accumulators_mutex:
        return self._accumulators[run]