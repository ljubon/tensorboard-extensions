from tensorboard.plugins import base_plugin
from .runsenabler_plugin import RunsEnablerPlugin

class RunsEnablerLoader(base_plugin.TBLoader):
    def __init__(self):
        self._plugin_class = RunsEnablerPlugin
    
    def define_flags(self, parser):
        group = parser.add_argument_group('runsenabler plugin')
        group.add_argument('--default_runs_regex', metavar='REGEX', type=str, default='', help='''\
            Specifies the regex by which to initialise the tensorboard runsenabler frontend with - no runs will be enabled by default but can be selected in the runsnenabler\
            ''')
        group.add_argument('--enable_profiling', metavar='ENABLENPROF', type=bool, default=False, help='''\
            Determines whether runsenabler will write stats to disk.\
            ''')

    def load(self, context):
        return self._plugin_class(context)
