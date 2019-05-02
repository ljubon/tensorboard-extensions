from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

from setuptools import find_packages, setup

CONSOLE_SCRIPTS = [
    'grtensorboard = gr_tensorboard.run.main_deployed:run',
]

REQUIRED_PACKAGES = [
    'tensorboard <= 1.12.0,>1.9',
    'tensorflow <= 1.12.0,>1.9'
]

setup(
    name='grtensorboard',
    version='0.0.15',
    description='GR-Tensorboard provides some extensions to vanilla Tensorboard via plugins',
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
        'gr_tensorboard.assets': [
            'assets.zip',
        ],
    },
    include_package_data=True,
    # Disallow python 3.0 and 3.1 which lack a 'futures' module (see above).
    python_requires='>=3.4.*',
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
    keywords='gresearch tensorflow tensorboard tensor machine learning visualizer',
)