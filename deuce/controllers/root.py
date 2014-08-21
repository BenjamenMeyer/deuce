from pecan import expose, redirect, response
from webob.exc import status_map

from deuce.controllers.vault import VaultController
from deuce.common.rbac import rbac_require, RBAC_OBSERVER, RBAC_CREATOR, RBAC_ADMIN


class RootController(object):

    def __init__(self):
        # Support multiple API versions from the beginning. This
        # should most likely get moved into config
        self.versions = {"v1.0": VaultController()}

    @rbac_require(permission_level=RBAC_OBSERVER)
    @expose(generic=True, template='index.html')
    def index(self):
        return dict()

    @rbac_require(permission_level=RBAC_OBSERVER)
    @expose()
    def _lookup(self, primary_key, *remainder):
        try:
            return self.versions[primary_key], remainder
        except KeyError:
            response.status_code = 404

    # TODO: Eliminate this error handling template or have
    # it return a well-formed error in a JSON body
    @rbac_require(permission_level=RBAC_OBSERVER)
    @expose('error.html')
    def error(self, status):
        try:
            status = int(status)
        except ValueError:  # pragma: no cover
            status = 500

        message = getattr(status_map.get(status), 'explanation', '')
        return dict(status=status, message=message)
