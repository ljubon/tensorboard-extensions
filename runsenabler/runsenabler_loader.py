from tensorboard.plugins import base_plugin
from .runsenabler_plugin import RunsEnablerPlugin

class RunsEnablerLoader(base_plugin.TBLoader):
    def __init__(self):
        self._plugin_class = RunsEnablerPlugin

    def load(self, context):
        return self._plugin_class(context)
