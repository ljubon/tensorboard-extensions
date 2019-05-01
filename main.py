from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import os
import sys
import shutil
from pathlib import PureWindowsPath

from tensorboard import default
from tensorboard import program
import tensorflow as tf

from .paramplot import paramplot_plugin
from .runsenabler import runsenabler_loader

def _is_dfs_path(logdir_path):
    """
    Returns true iff the path provided is contained within a network drive
    This makes some very strong assumptions about where the network drive is mounted and the structure of the filesystems
    """
    path_parts = PureWindowsPath(logdir_path).parts
    is_windows = sys.platform in ['win32', 'cygwin']
    return is_windows and ((len(path_parts) >= 3 and 'dfs' in path_parts[2].lower()) or (len(path_parts) >= 1 and "Q:" in path_parts[0]))

def run_main(asset_path, is_bazel):
    # Intialise the RunsEnabler loader with some default value. The original logdir will be set after arguments have been configured
    loader = runsenabler_loader.RunsEnablerLoader('some_dir', False)
    plugins = default.get_plugins() + [paramplot_plugin.ParamPlotPlugin, loader]

    tensorboard = program.TensorBoard(plugins, lambda: open(asset_path, 'rb'))
    tensorboard.configure(sys.argv)
    
    # Determine whether the log directory is located in a dfs mount - if so then the runsenabler should be disabled #meta
    runsenabler_enabled = not _is_dfs_path(tensorboard.flags.logdir)
    if runsenabler_enabled:
        # Retrieve the actual log directory and replace it in the context with the new logdir 
        original_logdir = tensorboard.flags.logdir
        parent_dir = os.path.dirname(original_logdir)
        print("logdir provided: " + original_logdir)
        new_logdir = os.path.join(parent_dir, 'temp_logdir')
        print("creating temporary workspace in " + new_logdir)

        # Create the temp dir
        os.makedirs(new_logdir)

        # swap the original logdir for the new one and enable the runsenabler (since the logdir is not in a network drive, we can create symlinks)
        # This is a sad hack to allow for the runsenabler to run in s
        loader._actual_logdir = original_logdir
        loader.enabled = runsenabler_enabled
        tensorboard.flags.logdir = new_logdir

    # Run tensorboard with the modified logdir (if runsenabler is enabled)
    try:
        sys.exit(tensorboard.main())
    finally:
        # Delete the temp logdir containing symbolic links to the original logdir runs if the runsenabler was enabled
        if runsenabler_enabled:
            shutil.rmtree(new_logdir)
