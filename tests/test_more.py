import json
import os
import sys
from datetime import datetime
from pathlib import Path
from types import SimpleNamespace, ModuleType

root = Path(__file__).resolve().parents[1]
sys.path.append(str(root))
sys.path.append(str(root / 'src'))

from ai.llm_service import LlmService
from ai.llm_executor import LlmExecutor
from ai.llm_models import NewTask, ModifiedTask, TaskChanges, FirestoreEncoder
from ai.prompt_repository import PromptRepository
from eval.eval_input_repository import EvalInputRepository


def create_service(monkeypatch):
    os.environ.setdefault('OPENAI_API_KEY', 'k')
    monkeypatch.setattr('ai.llm_service.get_client', lambda: SimpleNamespace())
    return LlmService()


def test_list_tasks(monkeypatch):
    service = create_service(monkeypatch)
    class T:
        def __init__(self, i):
            self.i = i
        def to_dict(self):
            return {'id': self.i}
    ts = SimpleNamespace(
        get_active_tasks=lambda u: [T('a')],
        get_completed_tasks=lambda u: [T('b')],
        get_deleted_tasks=lambda u: [T('c')]
    )
    monkeypatch.setattr('ai.llm_service.get_task_service', lambda: ts)
    result = service._list_tasks('u1')
    assert result == {'active': [{'id': 'a'}], 'completed': [{'id': 'b'}], 'deleted': [{'id': 'c'}]}


def test_get_system_prompt_fallback(monkeypatch):
    monkeypatch.setattr('ai.llm_service.get_prompt_repository', lambda: SimpleNamespace(get_active_prompt=lambda n: None))
    service = create_service(monkeypatch)
    prompt = service._get_system_prompt()
    assert prompt.prompt_name == 'AI_Tasks'
    assert prompt.version == 0
    assert prompt.text.startswith('You are an expert Task manager')


def test_update_task_success(monkeypatch):
    updates = []
    ts = SimpleNamespace(update_task=lambda u, t, d: updates.append((u, t, d)))
    monkeypatch.setattr('ai.llm_service.get_task_service', lambda: ts)
    service = create_service(monkeypatch)
    res = service._update_task('u1', 't1', json.dumps({'title': 'n'}))
    assert res == {'success': True}
    assert updates == [('u1', 't1', {'title': 'n'})]


def test_executor_third_call(monkeypatch):
    calls = {'c': [], 'u': []}
    class DummyTS:
        def create_task(self, uid, data):
            calls['c'].append((uid, data))
        def update_task(self, uid, tid, data):
            calls['u'].append((uid, tid, data))
    monkeypatch.setattr('ai.llm_executor.get_task_service', lambda: DummyTS())
    executor = LlmExecutor(SimpleNamespace())
    changes = TaskChanges(new_tasks=[NewTask(title='x')], modified_tasks=[ModifiedTask(id='m', title='y')])
    executor._LlmExecutor__third_call('u1', changes)
    assert calls['c'][0][0] == 'u1'
    assert calls['u'][0] == ('u1', 'm', {'title': 'y'})


def test_first_call_builds_prompt(monkeypatch):
    record = {}
    class DummyChat:
        def __init__(self, api_key=None, model=None, temperature=None):
            record['init'] = (api_key, model, temperature)
        def invoke(self, messages):
            record['messages'] = messages
            return SimpleNamespace(content='ok')
    monkeypatch.setattr('ai.llm_executor.ChatOpenAI', DummyChat)
    executor = LlmExecutor(SimpleNamespace(api_key='k', model='m'))
    result = executor._first_call('S', ' hi ', {'active': [], 'completed': []})
    assert result == 'ok'
    assert record['init'] == ('k', 'm', 0.7)
    assert 'Current active tasks' in record['messages'][0].content


def test_firestore_encoder(monkeypatch):
    class C:
        def __str__(self):
            return 'c'
    dt = datetime(2024, 1, 1)
    encoded = json.dumps({'d': dt, 'c': C()}, cls=FirestoreEncoder)
    data = json.loads(encoded)
    assert data == {'d': '2024-01-01T00:00:00', 'c': 'c'}


def test_task_roundtrip():
    from database.models import Task
    dt = datetime(2024, 1, 1)
    t = Task(id='1', user_id='u', title='a', description='b', due_date=dt, notes='n')
    d = t.to_dict()
    t2 = Task.from_dict(d)
    assert t2.user_id == 'u'
    assert t2.title == 'a'
    assert t2.description == 'b'
    assert t2.due_date == dt
    assert t2.notes == 'n'


def test_prompt_repo_set_active_version(monkeypatch):
    updates = []
    class DB:
        def query(self, *a, **k):
            return [{'id': '1', 'version': 1}, {'id': '2', 'version': 2}]
        def update(self, c, doc_id, data):
            updates.append((doc_id, data['status']))
    monkeypatch.setattr('ai.prompt_repository.get_client', lambda: DB())
    repo = PromptRepository()
    res = repo.set_active_version('p', 2)
    assert res is True
    assert updates == [('1', 'inactive'), ('2', 'active')]


def test_prompt_repo_set_active_version_notfound(monkeypatch):
    updates = []
    class DB:
        def query(self, *a, **k):
            return [{'id': '1', 'version': 1}]
        def update(self, c, doc_id, data):
            updates.append((doc_id, data['status']))
    monkeypatch.setattr('ai.prompt_repository.get_client', lambda: DB())
    repo = PromptRepository()
    res = repo.set_active_version('p', 2)
    assert res is False
    assert updates == [('1', 'inactive')]


def test_eval_input_repo_create(monkeypatch):
    captured = {}
    class DB:
        def create(self, coll, data):
            captured.update(data)
            return 'x'
    monkeypatch.setattr('eval.eval_input_repository.get_client', lambda: DB())
    repo = EvalInputRepository()
    res = repo.create_from_chat({'user_id': 'u', 'inputText': 't', 'Response': 'r'}, 'p')
    assert res == 'x'
    assert captured['user_id'] == 'u'
    assert captured['evalPrompt'] == 'p'
