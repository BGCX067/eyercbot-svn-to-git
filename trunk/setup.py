#!/usr/bin/env python3.1

from distutils.core import setup

import sys

DISTUTILS_DEBUG=True

if sys.version_info < (3, 1, 0):
    sys.stderr.write("EyeRCBot requires Python 3.1 or newer.\n")
    sys.exit(-1)

import os.path

plugins = [s for s in os.listdir('eyercbot/plugins') if
           os.path.exists(os.path.join('eyercbot/plugins', s, 'plugin.py'))]
print("Plugins", plugins)
packages= ["eyercbot", "eyercbot.httplib2", "eyercbot.plugins", "eyercbot.NLPlib"] + ['eyercbot.plugins.'+s for s in plugins]
#packages= ["eyercbot", "eyercbot.plugins"]
print("Packages", packages)

setup(name='eyercbot',
      version='2.9.9',
      description='IRC Bot',
      author='David Radford',
      author_email='croxis@yahoo.com',
      url='http://code.google.com/p/eyercbot/',
      license="BSD",
      packages= packages,
      #packages= ["eyercbot", "eyercbot.plugins"],
      #package_dir = {"eyercbot": "eyercbot",
                #'eyercbot.plugins': 'eyercbot/plugins',
      #        },
      scripts=["scripts/eyercbot.bat", "scripts/eyercbot", "scripts/eyercbot_setup.bat", "scripts/eyercbot_setup"],
      )

