import sys
from pathlib import Path
from types import SimpleNamespace, ModuleType

# Stub external dependencies before importing the module
sys.modules.setdefault('streamlit', ModuleType('streamlit'))
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

sys.path.append(str(Path(__file__).resolve().parents[1]))

from ai.openai_service import OpenAIService, TaskChanges


def test_call_openai(monkeypatch):
    monkeypatch.setenv('OPENAI_API_KEY', 'test-key')
    monkeypatch.setattr('ai.openai_service.firestore_client', SimpleNamespace())
    service = OpenAIService()

    monkeypatch.setattr(service, '_first_call', lambda sp, ui, tl: 'content')
    tc = TaskChanges(new_tasks=[], modified_tasks=[])
    monkeypatch.setattr(service, '_second_call', lambda c1: tc)
    monkeypatch.setattr(service, '_OpenAIService__third_call', lambda uid, r: 'done')

    result = service._call_openai('user', 'prompt', 'input', {})
    assert result == 'done'
