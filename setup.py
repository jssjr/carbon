#!/usr/bin/env python

import os
import platform
from glob import glob

from setuptools import setup
setup_kwargs = dict(zip_safe=0)

conf_files = [ ('share/carbon/conf', glob('conf/*.example')) ]

install_files = conf_files

# If we are building on RedHat, let's use the redhat init scripts.
if platform.dist()[0] == 'redhat':
    init_scripts = [ ('/etc/init.d', ['distro/redhat/init.d/carbon-cache',
                                      'distro/redhat/init.d/carbon-relay',
                                      'distro/redhat/init.d/carbon-aggregator']) ]
    install_files += init_scripts


setup(
  name='carbon',
  version='0.9.12',
  url='http://graphite-project.github.com',
  author='Chris Davis',
  author_email='chrismd@gmail.com',
  license='Apache Software License 2.0',
  description='Backend data caching and persistence daemon for Graphite',
  packages=['carbon', 'carbon.app', 'carbon.aggregator', 'twisted.plugins'],
  package_data={ 'carbon' : ['*.xml'] },
  data_files=install_files,
  install_requires=['twisted', 'txamqp', 'whisper'],
  entry_points={
      'console_scripts': [
          "carbon-cache=carbon.app.cache:run",
          "carbon-aggregator=carbon.app.aggregator:run",
          "carbon-client=carbon.app.client:run",
          "carbon-relay=carbon.app.relay:run",
          "validate-storage-schemas=carbon.app.validate_storage_schemas:run"
          ]
      }
#  **setup_kwargs
)
