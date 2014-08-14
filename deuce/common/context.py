import uuid
import six


class RequestContext(object):

    """Helper class to represent useful information about a request context.

    Stores information about request id per request made.
    """

    def __init__(self):
        self.request_id = 'req-' + str(uuid.uuid4())

    def decode(self, encoding='utf-8', errors='strict'):
        if six.PY2:
            return self.request_id.decode(encoding, errors)
        else:
            return str(six.b(self.request_id), encoding, errors)
