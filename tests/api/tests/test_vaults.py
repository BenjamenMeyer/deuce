from tests.api import base
import ddt


class TestNoVaultsCreated(base.TestBase):

    def setUp(self):
        super(TestNoVaultsCreated, self).setUp()

    def test_head_missing_vault(self):
        """Head of a vault that has not been created"""

        resp = self.client.vault_head(self.id_generator(50))
        self.assertEqual(resp.status_code, 404,
                         'Status code returned: {0} . '
                         'Expected 404'.format(resp.status_code))
        self.assertHeaders(resp.headers)
        self.assertEqual(len(resp.content), 0,
                         'Response Content was not empty. Content: '
                         '{0}'.format(resp.content))

    def test_get_missing_vault(self):
        """Get a vault that has not been created"""

        resp = self.client.get_vault(self.id_generator(50))
        self.assertEqual(resp.status_code, 404,
                         'Status code returned: {0} . '
                         'Expected 404'.format(resp.status_code))
        self.assertHeaders(resp.headers)

    def tearDown(self):
        super(TestNoVaultsCreated, self).tearDown()


@ddt.ddt
class TestCreateVaults(base.TestBase):

    def setUp(self):
        super(TestCreateVaults, self).setUp()

    @ddt.data(1, 10, 100, 128)
    def test_create_vaults(self, size):
        """Create a Vault"""

        self.vaultname = self.id_generator(size)
        resp = self.client.create_vault(self.vaultname)
        self.assertEqual(resp.status_code, 201,
                         'Status code returned for Create Vault: {0} . '
                         'Expected 201'.format(resp.status_code))
        self.assertHeaders(resp.headers)
        self.assertEqual(len(resp.content), 0,
                         'Response Content was not empty. Content: '
                         '{0}'.format(resp.content))

    def tearDown(self):
        super(TestCreateVaults, self).tearDown()
        if hasattr(self, 'vaultname'):
            self.client.delete_vault(self.vaultname)


class TestEmptyVault(base.TestBase):

    def setUp(self):
        super(TestEmptyVault, self).setUp()
        self.create_empty_vault()

    def test_get_vault(self):
        """Get an individual vault. Get the statistics for a vault"""

        resp = self.client.get_vault(self.vaultname)
        self.assertEqual(resp.status_code, 200,
                         'Status code returned for Get Vault: {0} . '
                         'Expected 200'.format(resp.status_code))
        self.assertHeaders(resp.headers, json=True)
        resp_body = resp.json()
        self.assertIn('storage', resp_body)
        self.assertIn('metadata', resp_body)

        storage = resp_body['storage']
        self.assertEqual(storage['block-count'], 0)
        self.assertEqual(storage['internal'], {})
        self.assertEqual(storage['total-size'], 0)

        meta = resp_body['metadata']
        self.assertIn('files', meta)
        self.assertIn('internal', meta)
        self.assertIn('blocks', meta)

        meta_files = meta['files']
        self.assertEqual(meta_files['count'], 0)

        self.assertEqual(meta['internal'], {})

        meta_blocks = meta['blocks']
        self.assertEqual(meta_blocks['count'], 0)

    def test_delete_vault(self):
        """Delete a Vault"""

        resp = self.client.delete_vault(self.vaultname)
        self.assertEqual(resp.status_code, 204,
                         'Status code returned for Delete Vault: {0} . '
                         'Expected 204'.format(resp.status_code))
        self.assertHeaders(resp.headers)
        self.assertEqual(len(resp.content), 0,
                         'Response Content was not empty. Content: '
                         '{0}'.format(resp.content))

    def test_vault_head(self):
        """Head of an individual vault"""

        resp = self.client.vault_head(self.vaultname)
        self.assertEqual(resp.status_code, 204,
                         'Status code returned for Vault HEAD: {0} . '
                         'Expected 204'.format(resp.status_code))
        self.assertHeaders(resp.headers)
        self.assertEqual(len(resp.content), 0,
                         'Response Content was not empty. Content: '
                         '{0}'.format(resp.content))

    def tearDown(self):
        super(TestEmptyVault, self).tearDown()
        self.client.delete_vault(self.vaultname)


class TestVaultWithBlocksFiles(base.TestBase):

    def setUp(self):
        super(TestVaultWithBlocksFiles, self).setUp()
        self.create_empty_vault()
        [self.upload_block() for _ in range(20)]
        [self.create_new_file() for _ in range(3)]
        # Assign specific blocks to the files created
        # Assign 3 unique blocks to file 1
        self.assign_blocks_to_file(blocks=[0, 1, 2],
                                   file_url=self.files[0].Url)

        # Assign 5 blocks to file 2, sharing 2 blocks with file 1
        self.assign_blocks_to_file(blocks=[4, 5, 0, 6, 2],
                                   file_url=self.files[1].Url)

        # Assign 8 unique blocks to file 3 and finalize it
        self.assign_blocks_to_file(blocks=range(10, 18),
                                   file_url=self.files[2].Url)
        self.finalize_file(file_url=self.files[2].Url)
        # 14 blocks have been assigned to 3 files

    def test_get_populated_vault(self):
        """Get the statistics of a populated vault"""

        resp = self.client.get_vault(self.vaultname)
        self.assertEqual(resp.status_code, 200,
                         'Status code returned for Get Vault: {0} . '
                         'Expected 200'.format(resp.status_code))
        self.assertHeaders(resp.headers, json=True)
        resp_body = resp.json()
        storage = resp_body['storage']
        self.assertEqual(storage['block-count'], 20)
        self.assertEqual(storage['internal'], {})
        self.assertEqual(storage['total-size'], 30720 * 20)

        meta = resp_body['metadata']
        meta_files = meta['files']
        self.assertEqual(meta_files['count'], 3)

        self.assertEqual(meta['internal'], {})

        meta_blocks = meta['blocks']
        self.assertEqual(meta_blocks['count'], 20)

    def tearDown(self):
        super(TestVaultWithBlocksFiles, self).tearDown()
        [self.client.delete_file(vaultname=self.vaultname,
            fileid=fileid.Id) for fileid in self.files]
        [self.client.delete_block(self.vaultname, block.Id) for block in
            self.blocks]
        self.client.delete_vault(self.vaultname)


class TestPopulatedVault(base.TestBase):

    def setUp(self):
        super(TestPopulatedVault, self).setUp()
        self.create_empty_vault()
        self.upload_block()

    def test_delete_populated_vault(self):
        """Delete a Vault that has some data. 1 block"""

        resp = self.client.delete_vault(self.vaultname)
        self.assertEqual(resp.status_code, 412,
                         'Status code returned for Delete Vault: {0} . '
                         'Expected 412'.format(resp.status_code))
        self.assertHeaders(resp.headers)
        self.assertEqual(len(resp.content), 0,
                         'Response Content was not empty. Content: '
                         '{0}'.format(resp.content))

    def tearDown(self):
        super(TestPopulatedVault, self).tearDown()
        [self.client.delete_block(self.vaultname, block.Id) for block in
            self.blocks]
        self.client.delete_vault(self.vaultname)
