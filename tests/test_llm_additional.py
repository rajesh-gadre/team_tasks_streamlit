import json
import os
import sys
from types import SimpleNamespace
from pathlib import Path
import pytest

root = Path(__file__).resolve().parents[1]
sys.path.append(str(root))
sys.path.append(str(root / 'src'))

from ai.llm_service import LlmService
from ai.llm_executor import LlmExecutor
from ai.llm_models import NewTask, ModifiedTask, TaskChanges


def create_service(monkeypatch):
    os.environ.setdefault('OPENAI_API_KEY', 'k')
    monkeypatch.setattr('ai.llm_service.get_client', lambda: SimpleNamespace())
    return LlmService()


class DummyChatError(Exception):
    pass


def test_second_call_raises(monkeypatch):
    class DummyChat:
        def __init__(self, *a, **k):
            pass
        def with_structured_output(self, *a, **k):
            return self
        def invoke(self, *a, **k):
            err = DummyChatError('boom')
            err.response = SimpleNamespace(status_code=500, headers={'h': 'v'}, json=lambda: {'e': 'x'}, text='t')
            raise err
    monkeypatch.setattr('ai.llm_executor.ChatOpenAI', DummyChat)
    executor = LlmExecutor(SimpleNamespace(api_key='k', model='m'))
    with pytest.raises(DummyChatError):
        executor._second_call('content')


def test_add_task_requires_title(monkeypatch):
    created = []
    ts = SimpleNamespace(create_task=lambda *a, **k: created.append(1))
    monkeypatch.setattr('ai.llm_service.get_task_service', lambda: ts)
    service = create_service(monkeypatch)
    res = service._add_task('u1', json.dumps({'description': 'd'}))
    assert res == {'error': 'Task title is required'}
    assert created == []


def test_add_task_success(monkeypatch):
    monkeypatch.setattr('ai.llm_service.get_task_service', lambda: SimpleNamespace(create_task=lambda u, d: 'tid'))
    service = create_service(monkeypatch)
    res = service._add_task('u1', json.dumps({'title': 'T'}))
    assert res == {'success': True, 'task_id': 'tid'}


def test_update_task_error(monkeypatch):
    def upd(u, t, d):
        raise RuntimeError('fail')
    monkeypatch.setattr('ai.llm_service.get_task_service', lambda: SimpleNamespace(update_task=upd))
    service = create_service(monkeypatch)
    res = service._update_task('u1', 't1', json.dumps({'title': 'n'}))
    assert res == {'error': 'fail'}


def test_third_call_handles_exception(monkeypatch):
    class TS:
        def create_task(self, u, d):
            pass
        def update_task(self, u, t, d):
            raise RuntimeError('bad')
    monkeypatch.setattr('ai.llm_executor.get_task_service', lambda: TS())
    executor = LlmExecutor(SimpleNamespace())
    changes = TaskChanges(new_tasks=[NewTask(title='x')], modified_tasks=[ModifiedTask(id='m', title='y')])
    res = executor._LlmExecutor__third_call('u1', changes)
    assert res is None
