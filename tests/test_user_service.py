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
    def create_user(self, email, tz, name=None):
        self.calls.append(('create', email, tz, name))
        rec = {'userId': 'n1', 'userEmail': email, 'userTZ': tz}
        if name:
            rec['userName'] = name
        return rec
    def update_user_timezone(self, user_id, tz):
        self.calls.append(('update_tz', user_id, tz))
        return True

class DummyRoleService:
    def __init__(self):
        self.calls = []
    def ensure_default_role(self, user_id):
        self.calls.append(user_id)
        return {'id': 'r1', 'userId': user_id, 'role': 'regular'}

def test_login_existing(monkeypatch):
    repo = DummyRepo()
    roles = DummyRoleService()
    monkeypatch.setattr('src.users.user_service.get_user_repository', lambda: repo)
    monkeypatch.setattr('src.users.user_service.get_user_role_service', lambda: roles)
    service = UserService()
    record = service.login('e')
    assert record['userId'] == 'u1'
    assert repo.calls == [('get', 'e')]
    assert roles.calls == ['u1']

def test_login_new(monkeypatch):
    repo = DummyRepo()
    roles = DummyRoleService()
    monkeypatch.setattr('src.users.user_service.get_user_repository', lambda: repo)
    monkeypatch.setattr('src.users.user_service.get_user_role_service', lambda: roles)
    service = UserService()
    record = service.login('n', 'Name')
    assert record['userTZ'] == 'America/Los_Angeles'
    assert repo.calls == [('get', 'n'), ('create', 'n', 'America/Los_Angeles', 'Name')]
    assert roles.calls == ['n1']

def test_update_timezone(monkeypatch):
    repo = DummyRepo()
    monkeypatch.setattr('src.users.user_service.get_user_repository', lambda: repo)
    monkeypatch.setattr('src.users.user_service.get_user_role_service', lambda: DummyRoleService())
    service = UserService()
    result = service.update_timezone('u1', 'UTC')
    assert result is True
    assert repo.calls[-1] == ('update_tz', 'u1', 'UTC')
