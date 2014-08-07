
import os
from deuce.tests import FunctionalTest
from deuce.drivers.blockstoragedriver import BlockStorageDriver
from deuce.drivers.disk import DiskStorageDriver
from deuce.tests.util import MockFile

from hashlib import md5

# TODO: Make this test generic -- it should not konw
# which particular driver it is testing.


class DiskStorageDriverTest(FunctionalTest):

    def create_driver(self):
        return DiskStorageDriver()

    def get_Auth_Token(self):
        return None, None

    def test_ancestry(self):
        driver = self.create_driver()

        assert isinstance(driver, BlockStorageDriver)
        assert isinstance(driver, object)

    def test_basic_construction(self):
        driver = self.create_driver()

    def test_vault_crud(self):
        storage_url, token = self.get_Auth_Token()

        driver = self.create_driver()

        storage_url, auth_token = self.get_Auth_Token()

        projectid = 'test_project_id'
        vaultid = 'test_vault_id'

        driver.delete_vault(projectid, vaultid, token)
        assert not driver.vault_exists(projectid, vaultid, token)

        # delete a non-empty vault.
        driver.create_vault(projectid, vaultid, token)
        block_id = 'baab'
        driver.store_block(projectid, vaultid, block_id, b' ',
            token)
        assert driver.block_exists(projectid, vaultid, block_id,
            token)
        assert not driver.delete_vault(projectid, vaultid, token)
        assert driver.vault_exists(projectid, vaultid, token)
        # Cleanup and delete again.
        driver.delete_block(projectid, vaultid, block_id, token)
        assert driver.delete_vault(projectid, vaultid, token)
        assert not driver.vault_exists(projectid, vaultid, token)

        # To create an existed vault.
        driver.create_vault(projectid, vaultid, token)
        driver.create_vault(projectid, vaultid, token)

        assert driver.vault_exists(projectid, vaultid, token)

        driver.delete_vault(projectid, vaultid, token)

        assert not driver.vault_exists(projectid, vaultid, token)

    def test_block_crud(self):
        storage_url, token = self.get_Auth_Token()

        driver = self.create_driver()

        block_size = 3000
        vault_id = 'block_crud_vault_test'
        projectid = 'test_project_id'

        driver.create_vault(projectid, vault_id, token)

        # Create a file-like object
        block_data = MockFile(block_size)

        # Test Invalid block_id, ie, wrong sha1 hash.
        try:
            driver.store_block(projectid, vault_id,
                "test_disk_trouble_file", os.urandom(10), token)
        except:
            assert True
        driver.delete_block(projectid, vault_id, "test_disk_trouble_file",
            token)

        # Test delete invalid block
        driver.delete_block(projectid, vault_id, "test_invalid_block_deletion",
            token)

        # Test valid block_id.
        block_id = block_data.sha1()
        driver.store_block(projectid, vault_id, block_id, block_data.read(),
            token)
        block_data.seek(0)

        assert driver.block_exists(projectid, vault_id, block_id,
            token)

        # Read back the block data and compare
        file_obj = driver.get_block_obj(projectid, vault_id, block_id,
            token)

        returned_data = file_obj.read()

        # Returned data should be exatly the same

        assert len(returned_data) == block_size
        assert returned_data == block_data._content

        driver.delete_block(projectid, vault_id, block_id, token)

        assert not driver.block_exists(projectid, vault_id, block_id,
            token)

        assert None == driver.get_block_obj(projectid,
            vault_id, 'invalid_block_id', token)

        assert driver.delete_vault(projectid, vault_id, token)

    def test_block_generator(self):
        storage_url, token = self.get_Auth_Token()

        driver = self.create_driver()

        block_size = 3000
        vault_id = 'generator_test'
        projectid = 'test_project_id'

        driver.create_vault(projectid, vault_id, token)

        # Test re-entrance
        driver.create_vault(projectid, vault_id, token)

        blocks = [MockFile(block_size) for x in range(0, 10)]

        orig_hash = md5()

        for block_data in blocks:
            orig_hash.update(block_data._content)

        orig_hex = orig_hash.hexdigest()

        block_ids = []
        for block_data in blocks:
            block_id = block_data.sha1()
            block_ids.append(block_id)
            driver.store_block(projectid, vault_id, block_id,
                block_data.read(), token)
            block_data.seek(0)

        # Now call the block generator.

        blockid_gen = block_ids[:]

        gen = driver.create_blocks_generator(projectid, vault_id, blockid_gen,
            token)

        fetched_data = list(gen)

        assert len(fetched_data) == len(blocks) == 10

        for x in range(0, len(fetched_data)):
            blocks[x].seek(0)
            assert fetched_data[x].read() == blocks[x].read()

        # Clenaup.
        for block_id in block_ids[:]:
            driver.delete_block(projectid, vault_id,
                block_id, token)
        assert driver.delete_vault(projectid, vault_id, token)
