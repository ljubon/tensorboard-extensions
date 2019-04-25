from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import os

from .main import run_main

if __name__ == '__main__':   
    dirname = os.path.dirname(__file__)
    assets = os.path.abspath(os.path.join(dirname, 'assets.zip'))
    
    run_main(assets, False)