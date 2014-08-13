
from pecan import conf, response

from deuce.model.block import Block
from deuce.model.file import File

import deuce
import uuid
import hashlib


class Vault(object):

    @staticmethod
    def get(vault_id):
        if deuce.storage_driver.vault_exists(
                vault_id=vault_id):
            return Vault(
                vault_id=vault_id)
        return None

    @staticmethod
    def create(vault_id):
        """Creates the vault with the specified vault_id"""
        deuce.storage_driver.create_vault(
            vault_id=vault_id)
        return Vault(
            vault_id=vault_id)

    def __init__(self, vault_id):
        self.project_id = deuce.context.project_id
        self.vault_id = vault_id

    def get_vault_statistics(self):
        # Get information about the vault
        # - number of files
        # - number of blocks
        # - number of file-blocks
        # - total size
        # - etc
        vault_stats = {}

        metadata_info = deuce.metadata_driver
        storage_info = deuce.storage_driver

        vault_stats['metadata'] = metadata_info.get_vault_statistics(
            self.project_id, self.vault_id)
        vault_stats['storage'] = storage_info.get_vault_statistics(
            vault_id=self.vault_id)

        return vault_stats

    def put_block(self, block_id, blockdata, data_len):

        # Validate the hash of the block data against block_id
        if hashlib.sha1(blockdata).hexdigest() != block_id:
            raise ValueError('Invalid Hash Value in the block ID')

        retval = deuce.storage_driver.store_block(
            vault_id=self.vault_id,
            block_id=block_id,
            block_data=blockdata)

        file_id = deuce.metadata_driver.register_block(
            self.project_id, self.vault_id, block_id, data_len)

        return retval

    def get_blocks(self, marker, limit):
        gen = deuce.metadata_driver.create_block_generator(
            self.project_id,
            self.vault_id, marker=marker, limit=limit)

        return (Block(self.project_id, self.vault_id, bid) for bid in gen)

    def get_block(self, block_id):
        obj = deuce.storage_driver.get_block_obj(
            vault_id=self.vault_id,
            block_id=block_id)

        return Block(self.project_id, self.vault_id,
            block_id, obj) if obj else None

    def get_block_length(self, block_id):
        return deuce.storage_driver.get_block_object_length(
            vault_id=self.vault_id,
            block_id=block_id)

    def get_blocks_generator(self, block_ids):
        return deuce.storage_driver.create_blocks_generator(
            vault_id=self.vault_id,
            block_gen=block_ids)

    def create_file(self):
        file_id = str(uuid.uuid4())
        file_id = deuce.metadata_driver.create_file(self.project_id,
            self.vault_id, file_id)

        return File(self.project_id, self.vault_id, file_id)

    def get_files(self, marker, limit):
        gen = deuce.metadata_driver.create_file_generator(
            self.project_id, self.vault_id, marker=marker,
            limit=limit, finalized=True)

        return (File(self.project_id, self.vault_id, bid, finalized=True)
            for bid in gen)

    def get_file(self, file_id):
        try:
            data = deuce.metadata_driver.get_file_data(self.project_id,
                self.vault_id, file_id)

        except:
            # TODO: Improve this. This could be very
            # dangerous and cause a lot of head-scratching.
            return None

        return File(self.project_id, self.vault_id, file_id, finalized=data[0])

    def get_file_length(self, file_id):
        return deuce.metadata_driver.file_length(self.project_id,
            self.vault_id, file_id)

    def delete(self):
        return deuce.storage_driver.delete_vault(
            vault_id=self.vault_id)

    def delete_file(self, file_id):
        return deuce.metadata_driver.delete_file(
            self.project_id, self.vault_id, file_id)
