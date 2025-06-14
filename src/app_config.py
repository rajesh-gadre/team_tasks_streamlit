import os

def build_auth_config(auth_type: str) -> dict:
    if auth_type == 'auth0':
        return {
            'domain': os.environ.get('AUTH0_DOMAIN'),
            'client_id': os.environ.get('AUTH0_CLIENT_ID'),
            'client_secret': os.environ.get('AUTH0_CLIENT_SECRET'),
            'redirect_uri': os.environ.get('AUTH0_CALLBACK_URL'),
        }
    return {
        'client_id': os.environ.get('GOOGLE_CLIENT_ID'),
        'client_secret': os.environ.get('GOOGLE_CLIENT_SECRET'),
        'redirect_uri': os.environ.get('GOOGLE_REDIRECT_URI'),
        'allow_insecure_http': True,
    }
