import sys
import json
from pathlib import Path
root = Path(__file__).resolve().parents[1]
sys.path.append(str(root))
sys.path.append(str(root / 'aws_lambda_api'))
from handler import handler

class DummyService:
    def __init__(self):
        self.calls = []
    def get_all_tasks_for_user(self, uid):
        self.calls.append(('list', uid))
        return [type('T', (), {'to_dict': lambda self: {'id': '1'}})()]
    def create_task(self, uid, data):
        self.calls.append(('create', uid, data))
        return '1'
    def get_task(self, uid, tid):
        self.calls.append(('get', uid, tid))
        return type('T', (), {'to_dict': lambda self: {'id': tid}})()
    def update_task(self, uid, tid, data):
        self.calls.append(('update', uid, tid, data))
        return True
    def delete_task(self, uid, tid):
        self.calls.append(('delete', uid, tid))
        return True

def _run(event, monkeypatch, service):
    monkeypatch.setattr('handler.get_task_service', lambda: service)
    return handler(event, None)

def test_list(monkeypatch):
    service = DummyService()
    event = {'httpMethod': 'GET', 'path': '/tasks', 'queryStringParameters': {'user_id': 'u'}}
    result = _run(event, monkeypatch, service)
    assert json.loads(result['body']) == [{'id': '1'}]
    assert service.calls == [('list', 'u')]

def test_create(monkeypatch):
    service = DummyService()
    event = {
        'httpMethod': 'POST',
        'path': '/tasks',
        'queryStringParameters': {'user_id': 'u'},
        'body': json.dumps({'title': 't'})
    }
    result = _run(event, monkeypatch, service)
    assert json.loads(result['body']) == {'id': '1'}
    assert service.calls[0][0] == 'create'

def test_update(monkeypatch):
    service = DummyService()
    event = {
        'httpMethod': 'PUT',
        'path': '/tasks/x',
        'queryStringParameters': {'user_id': 'u'},
        'body': json.dumps({'title': 't'})
    }
    result = _run(event, monkeypatch, service)
    assert json.loads(result['body']) == {'success': True}
    assert service.calls[0] == ('update', 'u', 'x', {'title': 't'})

