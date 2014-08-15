
from pecan.hooks import PecanHook
from pecan.core import abort


class AuthTokenHook(PecanHook):
    """Every request that hits Deuce must have a header specifying the
    auth_token for the user the request is for.

    If a request does not provide the header the request should fail
    with a 401"""

    def on_route(self, state):

        # Enforce the existence of the x-auth-token header and assign
        # the value to the request auth_token.
        try:
            # auth_token is assumed validated by an outside source (e.g Repose
            # or WSGI middleware
            state.request.auth_token = state.request.headers['x-auth-token']
        except KeyError:
            # Invalid request
            abort(401, comment="Missing Header : X-Auth-Token",
                  headers={'Transaction-ID': state.request.context.request_id})
