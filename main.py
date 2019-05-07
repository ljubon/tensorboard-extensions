from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import os
import sys
import shutil

from tensorboard import default
from tensorboard import program

if sys.version_info[0] < 3:
    from paramplot import paramplot_plugin
    from runsenabler import runsenabler_loader
    print(sys.version_info)
else:
    print(sys.version_info)
    from .paramplot import paramplot_plugin
    from .runsenabler import runsenabler_loader

def run_main(asset_path):
    # Intialise the RunsEnabler loader with some default value. The original logdir will be set after arguments have been configured
    loader = runsenabler_loader.RunsEnablerLoader('some_dir')
    plugins = default.get_plugins() + [paramplot_plugin.ParamPlotPlugin, loader]

    tensorboard = program.TensorBoard(plugins, lambda: open(asset_path, 'rb'))
    tensorboard.configure(sys.argv)
    
    # Determine whether the log directory is located in a dfs mount - if so then the runsenabler should be disabled #meta
    runsenabler_enabled = tensorboard.flags.enable_runsenabler
    if runsenabler_enabled:
        # Retrieve the actual log directory and replace it in the context with the new logdir 
        original_logdir = tensorboard.flags.logdir
        parent_dir = os.path.dirname(original_logdir)
        print("logdir provided: " + original_logdir)
        new_logdir = os.path.join(parent_dir, 'temp_logdir')
        print("creating temporary workspace in " + new_logdir)

        # Create the temp dir
        os.makedirs(new_logdir)

        # swap the original logdir for the new one
        loader._actual_logdir = original_logdir
        tensorboard.flags.logdir = new_logdir

    # Run tensorboard with the modified logdir (if runsenabler is enabled)
    try:
        sys.exit(tensorboard.main())
    finally:
        # Delete the temp logdir containing symbolic links to the original logdir runs if the runsenabler was enabled
        if runsenabler_enabled:
            shutil.rmtree(new_logdir)
