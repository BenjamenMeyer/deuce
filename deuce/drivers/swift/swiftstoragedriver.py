
from pecan import conf

import deuce
from deuce.drivers.blockstoragedriver import BlockStorageDriver

import os
import io
import shutil

import importlib
import hashlib

from swiftclient.exceptions import ClientException

from six import BytesIO


class SwiftStorageDriver(BlockStorageDriver):

    def __init__(self):
        self.lib_pack = importlib.import_module(
            conf.block_storage_driver.swift.swift_module)
        self.Conn = getattr(self.lib_pack, 'client')

    # =========== Context ==============================
    def update_context(self, request_headers, context):
        """Updates the context with the requirements for the driver"""
        class OpenStackSwiftContext(object):
            pass

        context.openstackswift = OpenStackSwiftContext()
        try:
            context.openstackswift.storage_url = request_headers['x-storage-url']
        except KeyError:
            return (401, 'Missing Header : X-Storage-URL')

        try:
            context.openstackswift.auth_token = request_headers['x-auth-token']
        except KeyError:
            return (401, 'Missing Header : X-Auth-Token')

    # =========== VAULTS ===============================
    def create_vault(self, vault_id):
        response = dict()

        try:
            self.Conn.put_container(
                url=deuce.context.openstackswift.storage_url,
                token=deuce.context.openstackswift.auth_token,
                container=vault_id,
                response_dict=response)
            return response['status'] == 201
        except (KeyError, ClientException) as e:
            return False

    def vault_exists(self, vault_id):
        try:
            ret = self.Conn.head_container(
                url=deuce.context.openstackswift.storage_url,
                token=deuce.context.openstackswift.auth_token,
                container=vault_id)
            return ret is not None
        except (KeyError, ClientException) as e:
            return False

    def get_vault_statistics(self, vault_id):
        """Return the statistics on the vault.

        "param vault_id: The ID of the vault to gather statistics for"""

        statistics = dict()
        statistics['internal'] = {}
        statistics['total-size'] = 0
        statistics['block-count'] = 0

        try:
            # This will always return a dictionary
            container_metadata = self.Conn.head_container(
                url=deuce.context.openstackswift.storage_url,
                token=deuce.context.openstackswift.auth_token,
                container=vault_id)

            mapper = {
                'total-size': 'x-container-bytes-used',
                'block-count': 'x-container-object-count'
            }
            mapper_internal = {
                'last-modification-time': 'x-timestamp'
            }

            for k, v in mapper.items():
                try:
                    statistics[k] = container_metadata[v]

                except KeyError:  # pragma: no cover
                    statistics[k] = 0

            for k, v in mapper_internal.items():
                try:
                    statistics['internal'][k] = container_metadata[v]

                except KeyError:  # pragma: no cover
                    statistics['internal'][k] = 0

        except ClientException as e:
            pass

        return statistics

    def delete_vault(self, vault_id):
        response = dict()
        try:
            self.Conn.delete_container(
                url=deuce.context.openstackswift.storage_url,
                token=deuce.context.openstackswift.auth_token,
                container=vault_id,
                response_dict=response)

            # 204 - successfully deleted the vault
            # 404 - vault did not exist to start with
            if response['status'] in (204, 404):

                # Successfully deleted the vault
                return True

            else:
                # Vault was not empty so it was not deleted
                # or
                # Unknown error
                return False

        except (KeyError, ClientException) as e:
            return False

    # =========== BLOCKS ===============================
    def store_block(self, vault_id, block_id, block_data):
        response = dict()
        try:
            mdhash = hashlib.md5()
            mdhash.update(block_data)
            mdetag = mdhash.hexdigest()
            ret_etag = self.Conn.put_object(
                url=deuce.context.openstackswift.storage_url,
                token=deuce.context.openstackswift.auth_token,
                container=vault_id,
                name='blocks/' + str(block_id),
                contents=block_data,
                content_length=len(block_data),
                etag=mdetag,
                response_dict=response)
            return response['status'] == 201 and ret_etag == mdetag
        except (KeyError, ClientException) as e:
            return False

    def block_exists(self, vault_id, block_id):
        try:
            ret = self.Conn.head_object(
                url=deuce.context.openstackswift.storage_url,
                token=deuce.context.openstackswift.auth_token,
                container=vault_id,
                name='blocks/' + str(block_id))
            return ret is not None
        except (KeyError, ClientException) as e:
            return False

    def delete_block(self, vault_id, block_id):
        response = dict()
        try:
            self.Conn.delete_object(
                url=deuce.context.openstackswift.storage_url,
                token=deuce.context.openstackswift.auth_token,
                container=vault_id,
                name='blocks/' + str(block_id),
                response_dict=response)
            return response['status'] >= 200 and response['status'] < 300
        except (KeyError, ClientException) as e:
            return False

    def get_block_obj(self, vault_id, block_id):
        response = dict()
        buff = BytesIO()
        try:
            ret_hdr, ret_obj_body = \
                self.Conn.get_object(
                    url=deuce.context.openstackswift.storage_url,
                    token=deuce.context.openstackswift.auth_token,
                    container=vault_id,
                    name='blocks/' + str(block_id),
                    response_dict=response)
            buff.write(ret_obj_body)
            buff.seek(0)
            return buff
        except (KeyError, ClientException) as e:
            return None

    def get_block_object_length(self, vault_id, block_id):
        """Returns the length of an object"""
        response = dict()
        try:
            ret_hdr, ret_obj_body = \
                self.Conn.get_object(
                    url=deuce.context.openstackswift.storage_url,
                    token=deuce.context.openstackswift.auth_token,
                    container=vault_id,
                    name='blocks/' + str(block_id),
                    response_dict=response)
            return ret_hdr['content-length']
        except ClientException as e:
            return 0

    def create_blocks_generator(self, vault_id, block_gen):
        """Returns a generator of file-like objects that are
        ready to read. These objects will get closed
        individually."""
        return (self.get_block_obj(vault_id, block_id)
            for block_id in block_gen)
