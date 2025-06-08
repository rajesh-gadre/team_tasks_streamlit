import sys
from pathlib import Path
sys.path.append(str(Path(__file__).resolve().parents[1]))
from src.users.user_service import UserService

class DummyRepo:
    def __init__(self):
        self.calls = []
    def get_by_email(self, email):
        self.calls.append(('get', email))
        if email == 'e':
            return {'userId': 'u1', 'userEmail': 'e', 'userTZ': 'Z'}
        return None
    def create_user(self, email, tz):
        self.calls.append(('create', email, tz))
        return {'userId': 'n1', 'userEmail': email, 'userTZ': tz}

def test_login_existing(monkeypatch):
    repo = DummyRepo()
    monkeypatch.setattr('src.users.user_service.get_user_repository', lambda: repo)
    service = UserService()
    record = service.login('e')
    assert record['userId'] == 'u1'
    assert repo.calls == [('get', 'e')]

def test_login_new(monkeypatch):
    repo = DummyRepo()
    monkeypatch.setattr('src.users.user_service.get_user_repository', lambda: repo)
    service = UserService()
    record = service.login('n')
    assert record['userTZ'] == 'America/Los_Angeles'
    assert repo.calls == [('get', 'n'), ('create', 'n', 'America/Los_Angeles')]
