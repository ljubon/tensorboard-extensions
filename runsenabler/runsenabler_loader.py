from tensorboard.plugins import base_plugin
from .runsenabler_plugin import RunsEnablerPlugin

class RunsEnablerLoader(base_plugin.TBLoader):
    def __init__(self):
        self._plugin_class = RunsEnablerPlugin
    
    def define_flags(self, parser):
        """ Adds RunsEnabler plugin command line arguments to CLI """
        group = parser.add_argument_group('runsenabler plugin')

        group.add_argument('--enable_runsenabler', metavar='ENABLERUNS', type=bool, default=False)

    def load(self, context):
        return self._plugin_class(context)
