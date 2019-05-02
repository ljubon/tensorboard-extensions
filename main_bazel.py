from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import os

import tensorflow as tf

from main import run_main

if __name__ == "__main__":
    assets = os.path.join(tf.resource_loader.get_data_files_path(), 'assets.zip')
    run_main(assets)