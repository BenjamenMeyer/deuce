import json

import falcon
from stoplight import validate

import deuce.util.log as logging
from deuce.model import Health
from deuce.transport.validation import *


logger = logging.getLogger(__name__)


class CollectionResource(object):

    @validate(req=RequestRule(), resp=ResponseRule())
    def on_get(self, req, resp):
        resp.body = json.dumps(Health.health())
