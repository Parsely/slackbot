from setuptools import setup
from pip.req import parse_requirements
import uuid

setup(
    name='parsely-slackbot',
    version='0.1dev',
    packages=['parsely_slackbot'],
    author='Parsely',
    author_email='support@parsely.com',
    scripts=['bin/parsely_slackbot'],
    license='Apache License 2.0',
    long_description=open('README.rst').read(),
    install_requires=[str(req.req) for req in parse_requirements('requirements.txt', session=uuid.uuid1())]
)