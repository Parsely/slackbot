from distutils.core import setup
from pip.req import parse_requirements
import uuid

setup(
    name='parsely-slackbot',
    version='0.1dev',
    packages=['parsely_slackbot'],
    author='Parsely',
    author_email='support@parsely.com',
    scripts=['bin/parsely_slackbot'],
    license='Creative Commons Attribution-Noncommercial-Share Alike license',
    long_description=open('Readme.md').read(),
    install_requires=[str(req.req) for req in parse_requirements('requirements.txt', session=uuid.uuid1())]
)