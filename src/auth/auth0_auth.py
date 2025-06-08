import os
import uuid
from typing import Tuple, Dict, Any
from authlib.integrations.requests_client import OAuth2Session

class Auth0Auth:

    def __init__(self, config: Dict[str, str]):
        self.domain = config['domain']
        self.client_id = config['client_id']
        self.client_secret = config['client_secret']
        self.redirect_uri = config['redirect_uri']
        self.scopes = config.get('scopes', 'openid profile email')
        self.authorization_endpoint = f'https://{self.domain}/authorize'
        self.token_endpoint = f'https://{self.domain}/oauth/token'
        self.userinfo_endpoint = f'https://{self.domain}/userinfo'
        self.session = OAuth2Session(client_id=self.client_id, client_secret=self.client_secret, scope=self.scopes, redirect_uri=self.redirect_uri)

    def get_authorization_url(self) -> Tuple[str, str]:
        url, state = self.session.create_authorization_url(self.authorization_endpoint)
        return (url, state)

    def get_user_info(self, query_params: Dict[str, Any], state: str) -> Dict[str, Any]:
        code = query_params.get('code')
        if not code:
            raise ValueError('Missing authorization code')
        self.session.fetch_token(self.token_endpoint, code=code, grant_type='authorization_code')
        resp = self.session.get(self.userinfo_endpoint)
        resp.raise_for_status()
        return resp.json()
auth0_auth = Auth0Auth({'domain': os.environ.get('AUTH0_DOMAIN', ''), 'client_id': os.environ.get('AUTH0_CLIENT_ID', ''), 'client_secret': os.environ.get('AUTH0_CLIENT_SECRET', ''), 'redirect_uri': os.environ.get('AUTH0_CALLBACK_URL', '')})
