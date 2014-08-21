from deuce.util import log as logging

from pecan import expose, response, request
from pecan.rest import RestController

import deuce

from deuce.controllers.blocks import BlocksController
from deuce.controllers.files import FilesController
from deuce.controllers.validation import *
from deuce.common.rbac import rbac_require, RBAC_OBSERVER, RBAC_CREATOR, RBAC_ADMIN
from deuce.model import Vault

logger = logging.getLogger(__name__)


class VaultController(RestController):

    blocks = BlocksController()
    files = FilesController()

    @rbac_require(permission_level=RBAC_OBSERVER)
    @expose()
    def index(self):
        logger.warning('Invalid vault controller index request')
        response.status_code = 404

    @validate(vault_name=VaultPutRule)
    @rbac_require(permission_level=RBAC_CREATOR)
    @expose()
    def put(self, vault_name):
        vault = Vault.create(vault_name, deuce.context.openstack.auth_token)
        # TODO: Need check and monitor failed vault.
        logger.info('Vault [{0}] created'.format(vault_name))
        response.status_code = 201 if vault else 500

    @validate(vault_id=VaultGetRule)
    @rbac_require(permission_level=RBAC_OBSERVER)
    @expose()
    def head(self, vault_id):
        """Returns the vault controller object"""

        if Vault.get(vault_id, deuce.context.openstack.auth_token):
            # weblint complains about the content-type header being
            # present as pecan doesn't intelligently add it or remove
            # it.
            del response.headers["Content-Type"]
            response.status_code = 204
            return response
        else:
            logger.error('Vault [{0}] does not exist'.format(vault_id))
            response.status_code = 404

    @validate(vault_id=VaultGetRule)
    @rbac_require(permission_level=RBAC_OBSERVER)
    @expose('json')
    def get_one(self, vault_id):
        """Returns the statistics on vault controller object"""

        vault = Vault.get(vault_id, deuce.context.openstack.auth_token)

        if vault:
            response.status_code = 200
            return vault.get_vault_statistics(
                deuce.context.openstack.auth_token)
        else:
            logger.error('Vault [{0}] does not exist'.format(vault_id))
            response.status_code = 404
            return None

    @validate(vault_id=VaultPutRule)
    @rbac_require(permission_level=RBAC_ADMIN)
    @expose()
    def delete(self, vault_id):
        vault = Vault.get(vault_id, deuce.context.openstack.auth_token)

        if vault:
            if vault.delete(
                    deuce.context.openstack.auth_token):
                logger.info('Vault [{0}] deleted'.format(vault_id))
                # weblint complains about the content-type header being present
                # as pecan doesn't intelligently add it or remove it.
                del response.headers["Content-Type"]
                response.status_code = 204

            else:
                logger.info('Vault [{0}] cannot be deleted'.format(vault_id))
                response.status_code = 412

        else:
            logger.error('Vault [{0}] deletion failed; '
                'Vault does not exist'.format(vault_id))
            response.status_code = 404
