from tests.api import base
import ddt


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
        self.assertIn('file-blocks', meta)

        meta_files = meta['files']
        self.assertEqual(meta_files['count'], 0)

        self.assertEqual(meta['internal'], {})

        meta_blocks = meta['blocks']
        self.assertEqual(meta_blocks['count'], 0)

        meta_file_blocks = meta['file-blocks']
        self.assertEqual(meta_file_blocks['count'], 0)

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
