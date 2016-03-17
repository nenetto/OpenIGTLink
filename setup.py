# Always prefer setuptools over distutils
from setuptools import setup, find_packages
# To use a consistent encoding
from codecs import open
from os import path

here = path.abspath(path.dirname(__file__))

# Get the long description from the README file
with open(path.join(here, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

#!/usr/bin/env python

from setuptools import setup, find_packages

__author__ = 'Eugenio Marinetto'

setup(
    name='OpenIGTLink',
    version='1.2.0',
    packages=find_packages(),
    description='Python server and client for OpenIGTLink connections',
    long_description=long_description,
    url='https://github.com/nenetto/OpenIGTLink',
    author='Eugenio Marinetto',
    author_email='emarinetto@hggm.es',
    license='GNU GENERAL PUBLIC LICENSE',
    keywords='igt, tracking, image-guided applications',
    install_requires=[  'threading',
                        'copy',
                        'numpy',
                        'struct',
                        'socket',
                        'pandas',
                        'time',
                        'signal',
                        'requests>=2.0,<=3.0',
                        'pyyaml',
                        'python-dateutil',
                        'pytz'],
)
