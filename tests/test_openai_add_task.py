import os
import json
import sys
from pathlib import Path
from types import SimpleNamespace

# ensure src is on path
sys.path.append(str(Path(__file__).resolve().parents[1] / 'src'))

from ai.openai_service import OpenAIService

# helper to create service with fake API key

def create_service(monkeypatch):
    os.environ.setdefault('OPENAI_API_KEY', 'test-key')
    monkeypatch.setattr('ai.openai_service.get_client', lambda: SimpleNamespace())
    return OpenAIService()

def test_add_task_valid(monkeypatch):
    service = create_service(monkeypatch)
    captured = {}

    class DummyTS:
        def create_task(self, user_id, task_data):
            captured['user_id'] = user_id
            captured['task_data'] = task_data
            return 'task123'

    monkeypatch.setattr('ai.openai_service.get_task_service', lambda: DummyTS())

    payload = {
        'title': 'New Task',
        'description': 'Do something',
        'notes': 'details',
        'due_date': '2024-01-01'
    }
    result = service._add_task('user1', json.dumps(payload))
    assert result == {'success': True, 'task_id': 'task123'}
    assert captured['user_id'] == 'user1'
    expected_payload = payload | {'status': 'active'}
    assert captured['task_data'] == expected_payload

def test_add_task_invalid(monkeypatch):
    service = create_service(monkeypatch)

    result = service._add_task('user1', json.dumps({'description': 'no title'}))
    assert result['error'] == 'Task title is required'
