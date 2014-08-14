
from deuce.drivers.blockstoragedriver import BlockStorageDriver
from deuce.drivers.swift import SwiftStorageDriver
from deuce.tests.test_disk_storage_driver import DiskStorageDriverTest

# Users need take care of authenticate themselves and
# have the token ready for each query.

from swiftclient import client as Conn
from swiftclient.exceptions import ClientException

from pecan import conf

import sys
import os
import json

import deuce

# TODO: Make this test generic -- it should not konw
# which particular driver it is testing.


class SwiftStorageDriverTest(DiskStorageDriverTest):

    def get_Auth_Token(self):

        auth_url = str(conf.block_storage_driver.swift.auth_url)

        username = 'User Name'
        password = 'Password'

        self.mocking = False
        try:
            if conf.block_storage_driver.swift.is_mocking:
                self.mocking = True
        except:
            self.mocking = False

        if not self.mocking:
            try:
                os_options = dict()
                storage_url, token = \
                    Conn.get_keystoneclient_2_0(
                        auth_url=auth_url,
                        user=username,
                        key=password,
                        os_options=os_options)
            except ClientException as e:
                sys.exit(str(e))

        else:
            storage_url = 'mocking_storage_url'
            token = 'mocking_token'

        return storage_url, token

    def get_mock_hdrs(self):
        storage_url, token = self.get_Auth_Token()
        project_id = storage_url[storage_url.rfind("/") + 1:]
        hdrs = self.create_mock_hdrs(
            project_id=project_id,
            storage_url=storage_url,
            auth_token=token)
        return hdrs

    def create_driver(self):
        return SwiftStorageDriver()

    def test_basic_construction(self):
        driver = self.create_driver()

    def test_ancestry(self):
        driver = self.create_driver()
        assert isinstance(driver, SwiftStorageDriver)
        assert isinstance(driver, object)

        # Test all exceptions
        hdrs = self.get_mock_hdrs()
        failed_hdrs = hdrs.copy()
        failed_hdrs['x-auth-token'] = failed_hdrs['x-auth-token'] + '1'
        driver = SwiftStorageDriver()
        driver.update_context(failed_hdrs, deuce.context)
        projectid = self.create_project_id()
        vaultid = self.create_vault_id()
        blockid = self.create_block_id()
        driver.create_vault(
            vault_id=vaultid)
        driver.vault_exists(
            vault_id=vaultid)
        driver.delete_vault(
            vault_id=vaultid)
        driver.store_block(
            vault_id=vaultid,
            block_id=blockid,
            block_data=str('').encode('utf-8'))
        driver.block_exists(
            vault_id=vaultid,
            block_id=blockid)
        driver.delete_block(
            vault_id=vaultid,
            block_id=blockid)
        driver.get_block_obj(
            vault_id=vaultid,
            block_id=blockid)

    def test_network_drops(self):
        """
        This is only to exercise code that relies on network errors to occur
        """
        self.mocking = False
        try:
            if conf.block_storage_driver.swift.is_mocking:
                self.mocking = True
        except:
            self.mocking = False

        if self.mocking:

            hdrs = self.get_mock_hdrs()
            driver = self.create_driver()
            driver.update_context(hdrs, deuce.context)
            vault_id = self.create_vault_id()
            block_id = self.create_block_id()

            assert isinstance(driver, SwiftStorageDriver)
            assert isinstance(driver, object)

            # simulate swiftclient tossing exceptions
            driver.Conn.mock_drop_connections(True)

            self.assertFalse(driver.create_vault(
                vault_id=vault_id))

            self.assertFalse(driver.vault_exists(
                vault_id=vault_id))

            self.assertFalse(driver.delete_vault(
                vault_id=vault_id))

            self.assertFalse(driver.store_block(
                vault_id=vault_id,
                block_id=block_id,
                block_data=str('').encode('utf-8')))

            self.assertFalse(driver.block_exists(
                vault_id=vault_id,
                block_id=block_id))

            self.assertFalse(driver.delete_block(
                vault_id=vault_id,
                block_id=block_id))

            self.assertIsNone(driver.get_block_obj(
                vault_id=vault_id,
                block_id=block_id))

            # Stats should come back as zero even though the connection
            # "dropped"
            bad_vault_stats = driver.get_vault_statistics(
                vault_id=vault_id)

            main_keys = ('total-size', 'block-count')
            for key in main_keys:
                assert key in bad_vault_stats.keys()
                assert bad_vault_stats[key] == 0

            # simulate swiftclient tossing exceptions
            driver.Conn.mock_drop_connections(False)
