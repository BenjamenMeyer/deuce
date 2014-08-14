from pecan.hooks import PecanHook
from pecan.core import abort

from deuce.common import local
from deuce.common import context

import deuce


def setup_deuce_context(request_headers):
    # Error handler for the drivers
    def check_results(ctx_results, transaction_id):
        if ctx_results is not None:
            abort(ctx_results[0], comment=ctx_results[1],
                  headers={'Transaction-ID': transaction_id})
    
    # Setup the context
    from threading import local as local_factory
    deuce.context = local_factory()

    # Setup the Transaction ID
    deuce.context.transaction = context.RequestContext()
    
    # Setup the Project Id
    try:
        deuce.context.project_id = request_headers['x-project-id']
    except KeyError:
        # Invalid request
        abort(400, comment="Missing Header : X-Project-ID",
              headers={'Transaction-ID': deuce.context.transaction})
    
    # Allow the MetaData driver to configure the context
    results = deuce.metadata_driver.update_context(request_headers,
        deuce.context)
    check_results(results, deuce.context.transaction)

    # Allow the Storage Driver to configure the context
    results = deuce.storage_driver.update_context(request_headers,
        deuce.context)
    check_results(results, deuce.context.transaction)

class DeuceHook(PecanHook):
    """Initialize the Deuce Context"""

    def on_route(self, state):
        setup_deuce_context(state.request.headers)

        setattr(local.store, 'context', deuce.context.transaction)
        state.request.context = deuce.context.transaction
