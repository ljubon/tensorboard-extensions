from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

from setuptools import find_packages, setup

CONSOLE_SCRIPTS = [
    'gr_tensorboard = gr_tensorboard.main_deployed',
]

REQUIRED_PACKAGES = [
    'tensorboard >= 1.12.0',
]

setup(
    name='gr_tensorboard',
    version='0.0.1',
    description='GR-Tensorboard provides some extensions to vanilla Tensorflow',
    long_description='',
    url='https://github.com/RMDev97/tensorboard-extensions',
    author='Ranjeev Menon',
    author_email='ranjeevmenon@hotmail.com',
    # Contained modules and scripts.
    packages=find_packages(),
    entry_points={
        'console_scripts': CONSOLE_SCRIPTS,
    },
    package_data={
        'gr_tensorboard': [
            'assets.zip',
        ],
    },
    # Disallow python 3.0 and 3.1 which lack a 'futures' module (see above).
    python_requires='>= 2.7, != 3.0.*, != 3.1.*',
    install_requires=REQUIRED_PACKAGES,
    # PyPI package information.
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'Intended Audience :: Education',
        'Intended Audience :: Science/Research',
        'License :: OSI Approved :: Apache Software License',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Topic :: Scientific/Engineering :: Mathematics',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Topic :: Software Development :: Libraries',
    ],
    license='Apache 2.0',
    keywords='tensorflow tensorboard tensor machine learning visualizer',
)