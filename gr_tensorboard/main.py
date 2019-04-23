# Copyright 2017 Google Inc. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import os
import sys
import shutil

from tensorboard import default
from tensorboard import program
import tensorflow as tf

from paramplot import paramplot_plugin
from runsenabler import runsenabler_loader

if __name__ == '__main__':
    # Intialise the RunsEnabler loader with some default value. The original logdir will be set after arguments have been configured
    assets = os.path.join(
        tf.resource_loader.get_data_files_path(), 'assets.zip')
    runsenabler_loader = runsenabler_loader.RunsEnablerLoader('some_dir')
    plugins = default.get_plugins(
    ) + [paramplot_plugin.ParamPlotPlugin, runsenabler_loader]

    tensorboard = program.TensorBoard(plugins, lambda: open(assets, 'rb'))
    tensorboard.configure(sys.argv)

    # Retrieve the actual log directory and replace it in the context with the new logdir
    original_logdir = tensorboard.flags.logdir
    parent_dir = os.path.abspath(os.path.join(original_logdir, os.pardir))
    new_logdir = os.path.join(parent_dir, 'temp_logdir')

    # Create the temp dir
    os.makedirs(new_logdir)

    # swap the original logdir for the new one
    runsenabler_loader._actual_logdir = original_logdir
    tensorboard.flags.logdir = new_logdir

    # Run tensorboard with the modified logdir
    try:
        sys.exit(tensorboard.main())
    finally:
        # Delete the temp logdir containing symbolic links to the original logdir runs
        shutil.rmtree(new_logdir)
