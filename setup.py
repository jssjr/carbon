#!/usr/bin/env python

import os
import platform
from carbon import __version__
from glob import glob

if os.environ.get('USE_SETUPTOOLS'):
  from setuptools import setup
  setup_kwargs = dict(zip_safe=0)

else:
  from distutils.core import setup
  setup_kwargs = dict()


storage_dirs = [
  ('storage/ceres', []),
  ('storage/whisper', []),
  ('storage/rrd', []),
  ('storage/log', []),
  ('storage/lists', []),
]
conf_files = [
  ('conf', glob('conf/*.example')),
  ('conf/carbon-daemons/example', glob('conf/carbon-daemons/example/*.conf')),
]

ceres_plugins = [('plugins/maintenance',glob('plugins/maintenance/*.py'))]

install_files = storage_dirs + conf_files + ceres_plugins

# If we are building on RedHat, let's use the redhat init scripts.
if platform.dist()[0] == 'redhat':
    init_scripts = [ ('/etc/init.d', ['distro/redhat/init.d/carbon-cache',
                                      'distro/redhat/init.d/carbon-relay',
                                      'distro/redhat/init.d/carbon-aggregator']) ]
    install_files += init_scripts

with open('README.md') as f:
    readme = f.read()
with open('LICENSE') as f:
    license = f.read()

setup(
  name='carbon',
  version=__version__,
  url='https://launchpad.net/graphite',
  author='Chris Davis',
  author_email='chrismd@gmail.com',
  license=license,
  description='Backend data caching and persistence daemon for Graphite',
  long_description=readme,
  packages=['carbon', 'carbon.aggregator', 'twisted.plugins'],
  scripts=glob('carbon/bin/*'),
  include_package_data = True,
  data_files=install_files,
  install_requires=['twisted', 'txamqp'],
  **setup_kwargs
)
