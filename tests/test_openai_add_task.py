import os
import json
import sys
from pathlib import Path
from types import SimpleNamespace, ModuleType
root_dir = Path(__file__).resolve().parents[1]
sys.path.append(str(root_dir))
sys.path.append(str(root_dir / 'src'))
sys.modules.setdefault('streamlit', ModuleType('streamlit'))
sys.modules['streamlit'].write = lambda *a, **k: None
sys.modules['streamlit'].session_state = {}
lc_core = ModuleType('langchain_core')
lc_core.pydantic_v1 = ModuleType('pydantic_v1')
lc_core.messages = ModuleType('messages')
import pydantic
lc_core.pydantic_v1.BaseModel = pydantic.BaseModel
lc_core.pydantic_v1.Field = lambda default=None, **kwargs: default

class _Msg:

    def __init__(self, content):
        self.content = content
lc_core.messages.SystemMessage = _Msg
lc_core.messages.HumanMessage = _Msg
sys.modules['langchain_core'] = lc_core
sys.modules['langchain_core.pydantic_v1'] = lc_core.pydantic_v1
sys.modules['langchain_core.messages'] = lc_core.messages
lc_openai = ModuleType('langchain_openai')

class DummyChat:

    def __init__(self, *a, **k):
        pass

    def with_structured_output(self, *a, **k):
        return self

    def invoke(self, *a, **k):
        return SimpleNamespace(content='ok')
lc_openai.ChatOpenAI = DummyChat
sys.modules['langchain_openai'] = lc_openai
from ai.llm_service import LlmService

def create_service(monkeypatch):
    os.environ.setdefault('OPENAI_API_KEY', 'test-key')
    monkeypatch.setattr('ai.llm_service.get_client', lambda: SimpleNamespace())
    return LlmService()

def test_add_task_valid(monkeypatch):
    service = create_service(monkeypatch)
    captured = {}

    class DummyTS:

        def create_task(self, user_id, task_data):
            captured['user_id'] = user_id
            captured['task_data'] = task_data
            return 'task123'
    monkeypatch.setattr('ai.llm_service.get_task_service', lambda: DummyTS())
    payload = {'title': 'New Task', 'description': 'Do something', 'notes': 'details', 'due_date': '2024-01-01'}
    result = service._add_task('user1', json.dumps(payload))
    assert result == {'success': True, 'task_id': 'task123'}
    assert captured['user_id'] == 'user1'
    expected_payload = payload | {'status': 'active'}
    assert captured['task_data'] == expected_payload

def test_add_task_invalid(monkeypatch):
    service = create_service(monkeypatch)
    result = service._add_task('user1', json.dumps({'description': 'no title'}))
    assert result['error'] == 'Task title is required'
