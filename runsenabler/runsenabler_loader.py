from tensorboard.plugins import base_plugin
from .runsenabler_plugin import RunsEnablerPlugin

class RunsEnablerLoader(base_plugin.TBLoader):
    def __init__(self):
        self._plugin_class = RunsEnablerPlugin
    
    def define_flags(self, parser):
        group = parser.add_argument_group('runsenabler plugin')
        group.add_argument('--enable_first_N_runs', metavar='ENABLENRUNS', type=int, default=50, help='''\
        Specifies how many of the most recent runs the user wants to be enabled by default (if not specified then this equals 50). 
        The actual number of runs which will be enabled on startup is min(*#Runs in logdir*, N) where N is the argument value.
        Providing a number less than 0 will enable all runs.\
        ''')

    def load(self, context):
        return self._plugin_class(context)
