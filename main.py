from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import os
import sys
import shutil

from tensorboard import default
from tensorboard import program
import tensorflow as tf

# from .paramplot import paramplot_plugin
# from .runsenabler import runsenabler_loader

def run_main(asset_path, is_bazel):

    # Added this to handle the discrepancy found when running this via bazel run vs from python directly
    if is_bazel:
        from paramplot import paramplot_plugin
        from runsenabler import runsenabler_loader
    else:
        from .paramplot import paramplot_plugin
        from .runsenabler import runsenabler_loader

    # Intialise the RunsEnabler loader with some default value. The original logdir will be set after arguments have been configured
    loader = runsenabler_loader.RunsEnablerLoader('some_dir')
    plugins = default.get_plugins(
    ) + [paramplot_plugin.ParamPlotPlugin, loader]

    tensorboard = program.TensorBoard(plugins, lambda: open(asset_path, 'rb'))
    tensorboard.configure(sys.argv)

    # Retrieve the actual log directory and replace it in the context with the new logdir
    original_logdir = tensorboard.flags.logdir
    parent_dir = os.path.abspath(os.path.join(original_logdir, os.pardir))
    new_logdir = os.path.join(parent_dir, 'temp_logdir')

    # Create the temp dir
    if not os.path.exists(new_logdir):
        os.makedirs(new_logdir)

    # swap the original logdir for the new one
    loader._actual_logdir = original_logdir
    tensorboard.flags.logdir = new_logdir

    # Run tensorboard with the modified logdir
    try:
        sys.exit(tensorboard.main())
    finally:
        # Delete the temp logdir containing symbolic links to the original logdir runs
        shutil.rmtree(new_logdir)
