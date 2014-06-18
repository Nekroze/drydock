#!/usr/bin/env python

import os
import sys

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup


if sys.argv[-1] == 'publish':
    os.system('python setup.py sdist upload')
    sys.exit()

readme = open('README.rst').read()
doclink = """
Documentation
-------------

The full documentation is at http://dry-dock.readthedocs.org."""

setup(
    name='drydock',
    version='0.6.9',
    description='A Docker cluster construction utility.',
    long_description=readme + '\n\n' + doclink,
    author='Taylor "Nekroze" Lawson',
    author_email='nekroze@eturnilnetwork.com',
    url='https://github.com/Nekroze/drydock',
    packages=[
        'drydock',
    ],
    package_dir={'drydock': 'drydock'},
    include_package_data=True,
    entry_points={
        'console_scripts': [
            'drydock = drydock.drydock:main',
        ]
    },
    install_requires=[
        "pyyaml>=3.10",
        "docopt>=0.6.1",
        "six>=1.5.2",
        "docker-py>=0.3.0",
    ],
    license='MIT',
    zip_safe=False,
    keywords='drydock',
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: Implementation :: PyPy',
    ],
)
