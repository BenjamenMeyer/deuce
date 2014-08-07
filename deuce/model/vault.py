
from pecan import conf, response

from deuce.model.block import Block
from deuce.model.file import File

import deuce
import uuid
import hashlib


class Vault(object):

    @staticmethod
    def get(project_id, vault_id, auth_token=None):

        if deuce.storage_driver.vault_exists(project_id, vault_id,
                auth_token=auth_token):
            return Vault(project_id, vault_id)

        return None

    @staticmethod
    def create(project_id, vault_id, auth_token=None):
        """Creates the vault with the specified vault_id"""
        deuce.storage_driver.create_vault(project_id, vault_id,
                auth_token=auth_token)
        return Vault(project_id, vault_id)

    def __init__(self, project_id, vault_id):
        self.project_id = project_id
        self.id = vault_id

    def put_block(self, block_id, blockdata, data_len,
            auth_token=None):

        # Validate the hash of the block data against block_id
        if hashlib.sha1(blockdata).hexdigest() != block_id:
            raise ValueError('Invalid Hash Value in the block ID')

        retval = deuce.storage_driver.store_block(
            self.project_id, self.id, block_id, blockdata,
            auth_token=auth_token)

        file_id = deuce.metadata_driver.register_block(
            self.project_id, self.id, block_id, data_len)

        return retval

    def get_blocks(self, marker, limit):
        gen = deuce.metadata_driver.create_block_generator(
            self.project_id,
            self.id, marker=marker, limit=limit)

        return (Block(self.project_id, self.id, bid) for bid in gen)

    def get_block(self, block_id, auth_token=None):
        obj = deuce.storage_driver.get_block_obj(self.project_id, self.id,
            block_id, auth_token=auth_token)

        return Block(self.project_id, self.id, block_id, obj) if obj else None

    def get_blocks_generator(self, block_ids, auth_token=None):
        return deuce.storage_driver.create_blocks_generator(
            self.project_id, self.id, block_ids,
            auth_token=auth_token)

    def create_file(self):
        file_id = str(uuid.uuid4())
        file_id = deuce.metadata_driver.create_file(self.project_id,
            self.id, file_id)

        return File(self.project_id, self.id, file_id)

    def get_files(self, marker, limit):
        gen = deuce.metadata_driver.create_file_generator(
            self.project_id, self.id, marker=marker,
            limit=limit, finalized=True)

        return (File(self.project_id, self.id, bid, finalized=True)
            for bid in gen)

    def get_file(self, file_id):
        try:
            data = deuce.metadata_driver.get_file_data(self.project_id,
                self.id, file_id)

        except:
            # TODO: Improve this. This could be very
            # dangerous and cause a lot of head-scratching.
            return None

        return File(self.project_id, self.id, file_id, finalized=data[0])

    def delete(self, auth_token=None):
        return deuce.storage_driver.delete_vault(self.project_id, self.id,
                auth_token=auth_token)

    def delete_file(self, file_id):
        return deuce.metadata_driver.delete_file(
            self.project_id, self.id, file_id)
