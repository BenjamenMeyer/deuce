from unittest import TestCase
from webtest import TestApp
from deuce.tests import FunctionalTest
import os

import json


class TestVaultController(FunctionalTest):

    def setUp(self):
        super(TestVaultController, self).setUp()
        self._hdrs = {"x-project-id": 'testvaultctrl',
            "x-auth-token": ''}

    def test_vault_leaf(self):
        response = self.app.get('/v1.0/', headers=self._hdrs,
            expect_errors=True)

        assert response.status_int == 404

    def test_invalid_vault_id(self):
        vault_name = '@#$@#$@$'
        vault_path = '/v1.0/{0}'.format(vault_name)

        response = self.app.put(vault_path, headers=self._hdrs,
                expect_errors=True)
        self.assertEqual(response.status_int, 400)

        response = self.app.get(vault_path, headers=self._hdrs,
                expect_errors=True)
        self.assertEqual(response.status_int, 404)

    def test_vault_crud(self):
        vault_name = 'my_new_vault'
        vault_path = '/v1.0/{0}'.format(vault_name)

        # If we try to get the vault before it exists, it should
        # return a 404
        response = self.app.get(vault_path,
            headers=self._hdrs, expect_errors=True)

        assert response.status_code == 404

        # Now we create the vault, which should return a 201 (created)
        response = self.app.put(vault_path, headers=self._hdrs)
        assert response.status_code == 201

        # Now if we get the vault, what do we get? For now,
        # let's enforce that we get a 204 (No Content)
        response = self.app.get(vault_path, headers=self._hdrs)

        assert response.status_code == 204

        # Now delete the vault (this should be OK since it
        # contains nothing in it.
        response = self.app.delete(vault_path, headers=self._hdrs,
            expect_errors=True)

        assert response.status_code == 204

        # Now we should get a 404 when trying to get the vault
        response = self.app.get(vault_path, headers=self._hdrs,
            expect_errors=True)

        assert response.status_code == 404

        # Try to delete again, this time it should be a 404
        response = self.app.delete(vault_path, headers=self._hdrs,
            expect_errors=True)

        assert response.status_code == 404
