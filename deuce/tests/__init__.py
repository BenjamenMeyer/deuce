import os
from unittest import TestCase
from pecan import set_config
import pecan
from pecan.testing import load_test_app

__all__ = ['FunctionalTest']

import shutil


conf_dict = {}


def setUp():
    """
        Unit tests environment setup.
        Called only once at the beginning.
    """
    global conf_dict
    if not os.path.exists('/tmp/block_storage'):
        os.mkdir('/tmp/block_storage')

    # Copy the production configs to the test path.
    if not os.path.exists('tests/public'):
        os.symlink('../../public', 'tests/public')
    if not os.path.exists('tests/deuce/templates'):
        if not os.path.exists('tests/deuce'):
            os.mkdir('tests/deuce')
        os.symlink('../../../deuce/templates', 'tests/deuce/templates')

    # Cook config.py for unit tests.
    prod_conf = pecan.configuration.conf_from_file('../config.py')
    conf_dict = prod_conf.to_dict()

    # To update existed items.
    conf_dict['metadata_driver']['mongodb']['db_module'] = \
        'deuce.tests.db_mocking.mongodb_mocking'
    conf_dict['metadata_driver']['mongodb']['FileBlockReadSegNum'] = 10
    conf_dict['metadata_driver']['mongodb']['maxFileBlockSegNum'] = 30
    # To add for-test-only items.
    # conf_dict['metadata_driver']['mongodb']['foo'] = 'bar'


def tearDown():
    """
        Unit tests environment cleanup.
        Called only once at the end.
    """
    shutil.rmtree('/tmp/block_storage')

    # Always remove the database so that we can start over on
    # test execution
    # Drop sqlite DB
    if os.path.exists('/tmp/deuce_sqlite_unittest_vaultmeta.db'):
        os.remove('/tmp/deuce_sqlite_unittest_vaultmeta.db')

    # Cleanup the test configs.
    if os.path.exists('tests/public'):
        os.remove('tests/public')
    if os.path.exists('tests/deuce/templates'):
        shutil.rmtree('tests/deuce')


class FunctionalTest(TestCase):
    """
    Used for functional tests where you need to test your
    literal application and its integration with the framework.
    """
    def setUp(self):
        global conf_dict
        self.app = load_test_app(config=conf_dict)

    def tearDown(self):
        set_config({}, overwrite=True)
