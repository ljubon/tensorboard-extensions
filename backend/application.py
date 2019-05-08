from tensorboard.plugins import base_plugin
from tensorboard.backend import application

from . import multiplexer

def gr_tensorboard_wsgi(flags, plugin_loaders, assets_zip_provider):
    controller = multiplexer.EventRunsController(size_guidance=application.DEFAULT_SIZE_GUIDANCE, logdir=flags.logdir)
    plugin_name_to_instance = {}
    context = base_plugin.TBContext(
        flags=flags,
        logdir=flags.logdir,
        multiplexer=controller,
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
    
    return application.TensorBoardWSGI(plugins, flags.path_prefix)