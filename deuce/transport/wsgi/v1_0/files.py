import json

from stoplight import validate

from deuce.util import set_qs_on_url
from deuce.model import Vault
from deuce import conf
import deuce.util.log as logging
from deuce.transport.validation import *
import deuce

logger = logging.getLogger(__name__)


class CollectionResource(object):

    @validate(req=RequestRule(FileMarkerRule,
                              LimitRule),
              vault_id=VaultGetRule)
    def on_get(self, req, resp, vault_id):
        vault = Vault.get(vault_id)

        if not vault:
            logger.error('Vault [{0}] does not exist'.format(vault_id))
            raise errors.HTTPNotFound
        # NOTE(TheSriram): get_param(param) automatically returns None
        # if param is not present
        inmarker = req.get_param('marker')
        limit = req.get_param_as_int('limit') if req.get_param_as_int('limit') \
            else conf.api_configuration.default_returned_num

        # The +1 is to fetch one past the user's
        # requested limit so that we can determine
        # if the list was truncated or not
        files = vault.get_files(inmarker, limit + 1)

        responses = list(files)

        # Note: the list may not actually be truncated
        truncated = len(responses) == limit + 1

        outmarker = responses.pop().file_id if truncated else None

        if outmarker:
            query_args = {'marker': outmarker}
            query_args['limit'] = limit

            returl = set_qs_on_url(req.url, query_args)

            resp.set_header("X-Next-Batch", returl)

        resp.body = json.dumps([response.file_id for response in responses])

    @validate(vault_id=VaultPutRule)
    def on_post(self, req, resp, vault_id):
        """Initializes a new file. The location of
        the new file is returned in the Location
        header
        """

        vault = Vault.get(vault_id)

        # caller tried to post to a vault that
        # does not exist
        if not vault:
            logger.error('Vault [{0}] does not exist'.format(vault_id))
            raise errors.HTTPNotFound

        file = vault.create_file()
        resp.set_header("Location", "{0}/{1}".format(req.url, file.file_id))
        resp.set_header("X-File-ID", file.file_id)
        resp.status = falcon.HTTP_201  # Created
        logger.info('File [{0}] created'.format(file.file_id))


class ItemResource(object):

    @validate(vault_id=VaultGetRule, file_id=FileGetRule)
    def on_get(self, req, resp, vault_id, file_id):
        """Fetches, re-assembles and streams a single
        file out of Deuce"""
        vault = Vault.get(vault_id)

        if not vault:
            logger.error('Vault [{0}] does not exist'.format(vault_id))
            raise errors.HTTPNotFound

        f = vault.get_file(file_id)

        if not f:
            logger.error('File [{0}] does not exist'.format(file_id))
            raise errors.HTTPNotFound

        if not f.finalized:
            raise errors.HTTPConflict('File not Finalized')

        block_gen = deuce.metadata_driver.create_file_block_generator(
            vault_id, file_id)

        block_ids = [block[0] for block in sorted(block_gen,
                                                  key=lambda block: block[1])]

        objs = vault.get_blocks_generator(block_ids)

        # NOTE(TheSriram): falcon 0.2.0 might fix this problem,
        # we should be able to set resp.stream to any file like
        # object instead of an iterator.

        def premature_close():
            raise StopIteration

        resp.stream = (obj.read() if obj else premature_close()
                       for obj in objs)
        resp.status = falcon.HTTP_200
        resp.set_header('Content-Length', str(vault.get_file_length(file_id)))
        resp.content_type = 'application/octet-stream'

    @validate(vault_id=VaultPutRule, file_id=FilePostRuleNoneOk)
    def on_post(self, req, resp, vault_id, file_id):
        """This endpoint finalizes a file
        """
        vault = Vault.get(vault_id)

        # caller tried to post to a vault that
        # does not exist
        if not vault:
            logger.error('Vault [{0}] does not exist'.format(vault_id))
            raise errors.HTTPBadRequestAPI('Vault does not exist')

        f = vault.get_file(file_id)

        if not f:
            logger.error('File [{0}] does not exist'.format(file_id))
            raise errors.HTTPNotFound

        if f.finalized:
            logger.error('Finalized file [{0}] '
                         'cannot be modified'.format(file_id))
            raise errors.HTTPConflict('Finalized file cannot be modified')
        try:

            filesize = int(req.get_header('x-file-length', required=True))
            res = deuce.metadata_driver.finalize_file(vault_id, file_id,
                                                      filesize)
        except Exception as e:
            # There are gaps or overlaps in blocks of the file
            # The list of errors returns
            details = str(e)
            logger.error('File [{0}] finalization '
                         'failed; [{1}]'.format(file_id, details))
            raise errors.HTTPConflict(json.dumps(details))
        else:
            resp.status = falcon.HTTP_200
            return

    @validate(vault_id=VaultGetRule, file_id=FileGetRule)
    def on_delete(self, req, resp, vault_id, file_id):

        vault = Vault.get(vault_id)
        if not vault:
            raise errors.HTTPNotFound

        f = vault.get_file(file_id)
        if not f:
            raise errors.HTTPNotFound

        vault.delete_file(file_id)
        resp.status = falcon.HTTP_204
