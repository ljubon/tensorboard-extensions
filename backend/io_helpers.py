import os
import re

def get_run_paths(logdir):
    """
    Returns a list of runs in the logdir path - i.e. any directory which contains a tf events file
    """
    return [root for root, _, files in os.walk(logdir) if any(re.search("events.out.tfevents.\d*.\w*", f) for f in files)]

def get_run_names(logdir):
    """
    Returns a list of run names in the logdir path
    """
    return [os.path.relpath(root, logdir) for root, _, files in os.walk(logdir) if any(re.search("events.out.tfevents.\d*.\w*", f) for f in files)]