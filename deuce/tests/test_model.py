import os.path

from unittest import TestCase
from webtest import TestApp
from deuce.tests import FunctionalTest

from deuce.model import Vault, Block, File

from deuce.hooks.deucehook import setup_deuce_context

class TestModel(FunctionalTest):

    def setUp(self):
        super(TestModel, self).setUp()

        self.storage_url = 'test_storage_url'
        self.project_id = self.create_project_id()
        self.hdrs = {'x-project-id': self.project_id}
        setup_deuce_context(self.hdrs)

    def test_get_nonexistent_block(self):
        v = Vault.get(
            vault_id='should_not_exist')
        assert v is None

    def test_vault_crud(self):
        vault_id = self.create_vault_id()

        v = Vault.get(
            vault_id=vault_id)
        assert v is None

        v = Vault.create(
            vault_id=vault_id)
        assert v is not None
        v.delete()

        v = Vault.get(
            vault_id=vault_id)
        assert v is None

    def test_file_crud(self):
        vault_id = self.create_vault_id()
        storage_url = ''

        v = Vault.create(
            vault_id=vault_id)

        f = v.create_file()

        assert isinstance(f, File)
        assert f.vault_id == vault_id

        file_id = f.file_id

        assert(len(file_id) > 0)

        file2 = v.get_file(file_id)
        file2_length = v.get_file_length(file_id)

        assert isinstance(file2, File)
        assert file2.file_id == file_id
        assert file2.project_id == self.project_id
        assert file2_length == 0

    def test_block_crud(self):
        vault_id = self.create_vault_id()

        v = Vault.create(
            vault_id=vault_id)

        # Check for blocks, should be none
        blocks_gen = v.get_blocks(0, 0)
        blocks_list = list(blocks_gen)

        assert len(blocks_list) == 0
