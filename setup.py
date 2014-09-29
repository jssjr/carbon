#!/usr/bin/env python

from __future__ import with_statement

import os
import ConfigParser

import platform
from glob import glob

from carbon import __version__

from setuptools import setup, find_packages
setup_kwargs = dict(zip_safe=0)

conf_files = [ ('conf', glob('conf/*.example')) ]

install_files = conf_files

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
  #packages=['carbon', 'carbon.app', 'carbon.aggregator', 'twisted.plugins'],
  packages=find_packages(exclude=['.tox', 'tests']),
  package_data={ 'carbon' : ['*.xml'] },
  data_files=install_files,
  install_requires=['twisted', 'txamqp'],
  test_suite='tests',
  entry_points={
      'console_scripts': [
          "carbon-cache=carbon.app.cache:run",
          "carbon-aggregator=carbon.app.aggregator:run",
          "carbon-client=carbon.app.client:run",
          "carbon-relay=carbon.app.relay:run",
          "validate-storage-schemas=carbon.app.validate_storage_schemas:run"
          ]
      },
  **setup_kwargs
)
