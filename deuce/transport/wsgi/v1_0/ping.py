import falcon
from stoplight import validate

from deuce.transport.validation import *
import deuce.util.log as logging


logger = logging.getLogger(__name__)


class CollectionResource(object):

    @validate(req=RequestRule(), resp=ResponseRule())
    def on_get(self, req, resp):
        resp.status = falcon.HTTP_204
