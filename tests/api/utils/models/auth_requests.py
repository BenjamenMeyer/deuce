from cafe.engine.models import base

import json


class AuthUsernameApiKey(base.AutoMarshallingModel):
    """
    Authenticate with Username and API Key Credentials
    """

    def __init__(self, username, api_key):
        super(AuthUsernameApiKey, self).__init__()
        self.username = username
        self.apikey = api_key

    def _obj_to_json(self):
        body_dict = {'auth':
            {'RAX-KSKEY:apiKeyCredentials':
                {'username': self.username, 'apiKey': self.apikey}}}
        return json.dumps(body_dict)
