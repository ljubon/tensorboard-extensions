import os

from tensorboard.plugins import base_plugin
from tensorboard.backend.event_processing import plugin_event_accumulator
from tensorboard.backend import application
from tensorboard.backend.event_processing import plugin_event_multiplexer

from .logging import _logger
import io_helpers

def gr_tensorboard_wsgi(flags, plugin_loaders, assets_zip_provider):
    size_guidance = {plugin_event_accumulator.TENSORS: 50}
    run_path_map = _getRunPathMapFromLogdir(flags.logdir, flags.enable_first_N_runs)
    _logger.log_message_info("loading EventMultiplexer with the %d most recent runs enabled by default" % flags.enable_first_N_runs)
    gr_multiplexer = plugin_event_multiplexer.EventMultiplexer(run_path_map=run_path_map,
                                                                size_guidance=size_guidance,
                                                                tensor_size_guidance=None,
                                                                purge_orphaned_data=True,
                                                                max_reload_threads=flags.max_reload_threads)
    _logger.log_message_info("Done loading EventMultiplexer")
    _logger.log_message_info("Loading all plugins.")
    plugin_name_to_instance = {}
    context = base_plugin.TBContext(
        flags=flags,
        logdir=flags.logdir,
        multiplexer=gr_multiplexer,
        assets_zip_provider=assets_zip_provider,
        plugin_name_to_instance=plugin_name_to_instance,
        window_title=flags.window_title)
    plugins = []
    for loader in plugin_loaders:
        plugin = loader.load(context)
        if plugin is None:
            continue
        plugins.append(plugin)
        plugin_name_to_instance[plugin.plugin_name] = plugin
    _logger.log_message_info("Done loading all plugins, now launching the tensorboard application")
    return application.TensorBoardWSGI(plugins, flags.path_prefix)

def _getRunPathMapFromLogdir(logdir, most_recent_num):
    if most_recent_num == 0:
        return {}
    elif most_recent_num > 0:
        dir_list = sorted(io_helpers.get_run_paths(logdir), key=os.path.getmtime)
        num_files = min(most_recent_num, len(dir_list))
        return {os.path.relpath(path, logdir): path for path in dir_list[-num_files:]}
    else:
        return {os.path.relpath(path, logdir): path for path in io_helpers.get_run_paths(logdir)}
