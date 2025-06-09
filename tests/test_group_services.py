import sys
from pathlib import Path
from types import SimpleNamespace

root = Path(__file__).resolve().parents[1]
sys.path.append(str(root))

from src.groups.group_service import GroupService
from src.groups.user_group_service import UserGroupService


class DummyRepo:
    def __init__(self):
        self.calls = []

    def get_groups(self):
        self.calls.append('get')
        return []

    def create_group(self, data):
        self.calls.append(('create', data))
        return 'id'

    def update_group(self, gid, data):
        self.calls.append(('update', gid, data))
        return True


class DummyUserGroupRepo:
    def __init__(self):
        self.calls = []

    def get_user_groups(self):
        self.calls.append('get')
        return []

    def create_user_group(self, data):
        self.calls.append(('create', data))
        return 'id'

    def update_user_group(self, uid, data):
        self.calls.append(('update', uid, data))
        return True

    def delete_user_group(self, uid):
        self.calls.append(('delete', uid))
        return True


def test_group_service(monkeypatch):
    repo = DummyRepo()
    monkeypatch.setattr('src.groups.group_service.get_group_repository', lambda: repo)
    service = GroupService()
    service.get_groups()
    service.create_group('n')
    service.update_group('g', 'n2')
    assert repo.calls == ['get', ('create', {'groupName': 'n'}), ('update', 'g', {'groupName': 'n2'})]


def test_user_group_service(monkeypatch):
    repo = DummyUserGroupRepo()
    monkeypatch.setattr('src.groups.user_group_service.get_user_group_repository', lambda: repo)
    service = UserGroupService()
    service.get_user_groups()
    service.create_user_group({'a': 1})
    service.update_user_group('u', {'b': 2})
    service.delete_user_group('u')
    assert repo.calls == ['get', ('create', {'a': 1}), ('update', 'u', {'b': 2}), ('delete', 'u')]
