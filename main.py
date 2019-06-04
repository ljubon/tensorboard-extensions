from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import sys

from tensorboard import default
from tensorboard.program import TensorBoard
# from .backend import program

if sys.version_info[0] < 3:
    from paramplot import paramplot_plugin
    from runsenabler import runsenabler_loader
    print(sys.version_info)
else:
    print(sys.version_info)
    from .paramplot import paramplot_plugin
    from .runsenabler import runsenabler_loader

def run_main(asset_path):
    plugins = default.get_plugins() + [paramplot_plugin.ParamPlotPlugin, runsenabler_loader.RunsEnablerLoader()]
    gr_tensorboard = TensorBoard(plugins, lambda: open(asset_path, 'rb'))
    gr_tensorboard.configure(sys.argv)

    sys.exit(gr_tensorboard.main())


