#!/usr/bin/env python
"""
Copyright 2014-2015 Parsely, Inc.

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
"""
from setuptools import setup


def readme():
    ''' Returns README.rst contents as str '''
    with open('README.rst') as f:
        return f.read()


tests_require = ['pytest', 'mock']
setup_requires = ['pytest-runner']
install_requires = ['Flask-Slack>=0.1.5',
                    'python-parsely',  # >= 1.5
                    'tzlocal>=1.2',
                    'requests',
                    'tornado']


setup(name='parsely-slackbot',
      version='1.0.2',
      author='Parsely, Inc.',
      author_email='support@parsely.com',
      url='https://github.com/Parsely/slackbot',
      description=('Parsely slackbot is a slack custom integration that uses '
                   'the Parsely API to allow realtime Slackalytics in your '
                   'Slack instance.'),
      long_description=readme(),
      license='Apache License 2.0',
      packages=['parsely_slackbot'],
      entry_points={'console_scripts':
                    ['parsely_slackbot = parsely_slackbot.app:main']},
      install_requires=install_requires,
      tests_require=tests_require,
      setup_requires=setup_requires,
      extras_require={'test': tests_require,
                      'all': install_requires + tests_require})
