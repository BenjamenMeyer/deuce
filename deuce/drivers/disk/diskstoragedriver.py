from pecan import conf
from deuce.drivers.blockstoragedriver import BlockStorageDriver

import os
import io
import shutil


class DiskStorageDriver(BlockStorageDriver):

    """A driver for storing blocks onto local disk

    IMPORTANT: This driver should not be considered
    secure and therefore should not be ran in
    any production environment.
    """

    def __init__(self):
        # Load the pecan config
        self._path = conf.block_storage_driver.options.path

    def _get_vault_path(self, project_id, vault_id):
        return os.path.join(self._path, str(project_id), vault_id)

    def _get_block_path(self, project_id, vault_id, block_id):
        vault_path = self._get_vault_path(project_id, vault_id)
        return os.path.join(vault_path, str(block_id))

    def create_vault(self, project_id, vault_id):
        path = self._get_vault_path(project_id, vault_id)

        if not os.path.exists(path):
            shutil.os.makedirs(path)

    def vault_exists(self, project_id, vault_id):
        path = self._get_vault_path(project_id, vault_id)
        return os.path.exists(path)

    def get_vault_statistics(self, project_id, vault_id):
        """Return the statistics on the vault.

        "param vault_id: The ID of the vault to gather statistics for"""
        res = {}

        # TODO: Add any statistics regarding files
        res['files'] = {}
        res['files']['count'] = 0

        # TODO: Add any statistics regarding blocks
        res['blocks'] = {}
        res['blocks']['count'] = 0

        # TODO: Add any statistics specific to the Disk backend
        res['internal'] = {}
        # res['internal']

        return res

    def delete_vault(self, project_id, vault_id):
        path = self._get_vault_path(project_id, vault_id)
        try:
            os.rmdir(path)
            return True
        except:
            return False

    def store_block(self, project_id, vault_id, block_id, blockdata):
        path = self._get_block_path(project_id, vault_id, block_id)

        with open(path, 'wb') as outfile:
            outfile.write(blockdata)

        return True

    def block_exists(self, project_id, vault_id, block_id):
        path = self._get_block_path(project_id, vault_id, block_id)
        return os.path.exists(path)

    def delete_block(self, project_id, vault_id, block_id):
        path = self._get_block_path(project_id, vault_id, block_id)

        if os.path.exists(path):
            os.remove(path)

    def get_block_obj(self, project_id, vault_id, block_id):
        """Returns a file-like object capable or streaming the
        block data. If the object cannot be retrieved, the list
        of objects should be returned
        """
        path = self._get_block_path(project_id, vault_id, block_id)

        if not os.path.exists(path):
            return None

        return open(path, 'rb')
