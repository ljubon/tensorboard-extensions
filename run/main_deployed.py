from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import os

from gr_tensorboard.main import run_main

def run():
    dirname = os.path.abspath(os.path.join(os.path.dirname(__file__), os.path.pardir))
    assets = os.path.abspath(os.path.join(dirname, 'assets', 'assets.zip'))
    run_main(assets)
