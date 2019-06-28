from tensorboard.plugins import base_plugin
from .runsenabler_plugin import RunsEnablerPlugin

from .runsenabler_controller import EventMultiplexerRunsController, FilesystemRunsController

class RunsEnablerLoader(base_plugin.TBLoader):
    def __init__(self, logdir):
        self._plugin_class = RunsEnablerPlugin
        self.actual_logdir = logdir
    
    def define_flags(self, parser):
        group = parser.add_argument_group('runsenabler plugin')
        group.add_argument('--default_runs_regex', metavar='REGEX', type=str, default='', help='''\
            Specifies the regex by which to initialise the tensorboard runsenabler frontend with - no runs will be enabled by default but can be selected in the runsnenabler\
            ''')
        group.add_argument('--enable_profiling', default=False, help='''\
            Determines whether runsenabler will write stats to disk.\
            ''', action='store_true')
        group.add_argument("--use_filesystem_controller", default=True, action='store_true')

    def load(self, context):
        # Determine which controller to use - either use the multiplexer directly or manipulate runs at the the filesystem level
        controller = EventMultiplexerRunsController(context.multiplexer, context.logdir)
        if context.flags.use_filesystem_controller:
            controller = FilesystemRunsController(self.actual_logdir, controller)
        return self._plugin_class(context, controller)
