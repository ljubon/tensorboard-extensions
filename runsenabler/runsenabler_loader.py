from tensorboard.plugins import base_plugin
from runsenabler import runsenabler_plugin

class RunsEnablerLoader(base_plugin.TBLoader):
    def __init__(self, actual_logdir):
        self._plugin_class = runsenabler_plugin.RunsEnablerPlugin
        self._actual_logdir = actual_logdir
    
    def load(self, context):
        return self._plugin_class(context, self._actual_logdir)