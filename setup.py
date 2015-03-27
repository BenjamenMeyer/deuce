# -*- coding: utf-8 -*-
import sys

from setuptools import setup, find_packages

REQUIRES = [
    'setuptools >= 1.1.6', 'aiohttp', 'asyncio',
    'configobj', 'falcon', 'stoplight', 'six',
    'python-swiftclient', 'msgpack-python',
    'cassandra-driver', 'pymongo',
]

DESCRIPTION = 'Deuce - Block-level de-duplication as-a-service'

DATA_FILES = [
    ('config', [
        'ini/config.ini',
        'ini/configspec.ini'
    ])
]

ENTRY_POINTS = {
    'console_scripts': [
        'deuce-server = deuce.cmd.server:run',
    ]
}

PACKAGE_EXCLUSIONS = [
    'tests*',
    'deuce/tests*'
]

setup(
    name='deuce',
    version='0.2',
    description=DESCRIPTION,
    license='Apache License 2.0',
    url='github.com/rackerlabs/deuce',
    author='Rackspace',
    author_email='',
    install_requires=REQUIRES,
    test_suite='deuce',
    zip_safe=False,
    entry_points=ENTRY_POINTS,
    data_files=DATA_FILES,
    packages=find_packages(exclude=PACKAGE_EXCLUSIONS)
)
