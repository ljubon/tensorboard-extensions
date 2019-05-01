from tensorboard.plugins import base_plugin
from .runsenabler_plugin import RunsEnablerPlugin


class RunsEnablerLoader(base_plugin.TBLoader):
    def __init__(self, actual_logdir, enabled):
        self._plugin_class = RunsEnablerPlugin
        self._actual_logdir = actual_logdir
        self.enabled = enabled

    def load(self, context):
        return self._plugin_class(context, self._actual_logdir, self.enabled)
