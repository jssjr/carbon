#!/usr/bin/env python

from __future__ import with_statement

import os
import ConfigParser

import platform
from glob import glob

from carbon import __version__

try:
    from io import BytesIO
except ImportError:
    from StringIO import StringIO as BytesIO

if os.environ.get('USE_SETUPTOOLS'):
  from setuptools import setup
  setup_kwargs = dict(zip_safe=0)

else:
  from distutils.core import setup
  setup_kwargs = dict()


storage_dirs = [ ('storage/whisper',[]), ('storage/lists',[]),
                 ('storage/log',[]), ('storage/rrd',[]) ]
conf_files = [ ('conf', glob('conf/*.example')) ]

install_files = storage_dirs + conf_files

# If we are building on RedHat, let's use the redhat init scripts.
if platform.dist()[0] == 'redhat':
    init_scripts = [ ('/etc/init.d', ['distro/redhat/init.d/carbon-cache',
                                      'distro/redhat/init.d/carbon-relay',
                                      'distro/redhat/init.d/carbon-aggregator']) ]
    install_files += init_scripts

setup(
  name='carbon',
  version=__version__,
  url='https://launchpad.net/graphite',
  author='Chris Davis',
  author_email='chrismd@gmail.com',
  license='Apache Software License 2.0',
  description='Backend data caching and persistence daemon for Graphite',
  long_description='Backend data caching and persistence daemon for Graphite',
  packages=['carbon', 'carbon.aggregator', 'twisted.plugins'],
  scripts=glob('bin/*'),
  package_data={ 'carbon' : ['*.xml'] },
  data_files=install_files,
  install_requires=['twisted', 'txamqp'],
  **setup_kwargs
)
