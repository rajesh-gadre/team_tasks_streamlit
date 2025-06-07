import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[1]))

import types

# Provide a minimal stub for the streamlit module used in google_auth
sys.modules.setdefault('streamlit', types.ModuleType('streamlit'))
sys.modules['streamlit'].session_state = {}

from src.auth.google_auth import get_google_auth


def _create_auth(monkeypatch):
    monkeypatch.setenv('GOOGLE_CLIENT_ID', 'client')
    monkeypatch.setenv('GOOGLE_CLIENT_SECRET', 'secret')
    monkeypatch.setenv('JWT_SECRET_KEY', 'jwt-secret')
    return get_google_auth()


def test_generate_and_validate_token(monkeypatch):
    auth = _create_auth(monkeypatch)
    user_info = {'id': '123', 'email': 'user@example.com', 'name': 'User'}
    token = auth.generate_token(user_info)
    assert isinstance(token, str)
    valid, payload = auth.validate_token(token)
    assert valid is True
    assert payload['email'] == 'user@example.com'
    assert payload['id'] == '123'


def test_invalid_token(monkeypatch):
    auth = _create_auth(monkeypatch)
    valid, payload = auth.validate_token('invalid')
    assert valid is False
    assert payload is None
