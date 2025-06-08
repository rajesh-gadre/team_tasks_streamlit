import os
import sys
from pathlib import Path
from types import SimpleNamespace, ModuleType
from unittest.mock import MagicMock
import pytest
root_dir = Path(__file__).resolve().parents[1]
sys.path.append(str(root_dir))
sys.path.append(str(root_dir / 'src'))
lc_core = ModuleType('langchain_core')
lc_core.messages = ModuleType('messages')

class _Msg:

    def __init__(self, content):
        self.content = content
lc_core.messages.SystemMessage = _Msg
lc_core.messages.HumanMessage = _Msg
sys.modules['langchain_core'] = lc_core
sys.modules['langchain_core.messages'] = lc_core.messages
lc_openai = ModuleType('langchain_openai')

class DummyChat:

    def __init__(self, *a, **k):
        pass

    def invoke(self, *a, **k):
        return SimpleNamespace(content='ok')
lc_openai.ChatOpenAI = DummyChat
sys.modules['langchain_openai'] = lc_openai
from src.eval.eval_service import EvalService
from src.eval.eval_input_service import EvalInputService
from src.database.models import AIEvalInput, AIPrompt

def _setup_eval_service(monkeypatch):
    repo = MagicMock()
    repo.create_result.return_value = 'rid'
    prompt_repo = MagicMock()
    prompt_repo.get_prompt_by_name_version.return_value = AIPrompt(prompt_name='p', text='t', version=1)
    monkeypatch.setattr('src.eval.eval_service.get_eval_result_repository', lambda: repo)
    monkeypatch.setattr('src.eval.eval_service.get_prompt_repository', lambda: prompt_repo)
    monkeypatch.setenv('OPENAI_API_KEY', 'k')
    return (EvalService(), repo, prompt_repo)

def _setup_input_service(monkeypatch):
    repo = MagicMock()
    db = MagicMock()
    monkeypatch.setattr('src.eval.eval_input_service.get_eval_input_repository', lambda: repo)
    monkeypatch.setattr('src.eval.eval_input_service.get_client', lambda: db)
    return (EvalInputService(), repo, db)

def test_run_evals(monkeypatch):
    service, repo, prepo = _setup_eval_service(monkeypatch)
    ev = AIEvalInput(id='i1', user_id='u', input_text='q')
    result = service.run_evals('p', 1, [ev])
    assert result == ['rid']
    repo.create_result.assert_called_once()
    prepo.get_prompt_by_name_version.assert_called_once_with('p', 1)

def test_run_evals_missing_prompt(monkeypatch):
    service, repo, prepo = _setup_eval_service(monkeypatch)
    prepo.get_prompt_by_name_version.return_value = None
    with pytest.raises(ValueError):
        service.run_evals('p', 1, [])

def test_eval_input_service_calls(monkeypatch):
    service, repo, db = _setup_input_service(monkeypatch)
    service.get_latest_inputs(5)
    repo.get_latest_inputs.assert_called_once_with(5)
    service.add_from_chat({'id': 'c1'}, 'p')
    repo.create_from_chat.assert_called_once_with({'id': 'c1'}, 'p')
    db.delete.assert_called_once_with('AI_chats', 'c1')
    service.update_status('x', 'archived')
    repo.update_status.assert_called_once_with('x', 'archived')

def test_eval_input_update(monkeypatch):
    service, repo, _ = _setup_input_service(monkeypatch)
    service.update_input('x', {'inputText': 'n'})
    repo.update_input.assert_called_once_with('x', {'inputText': 'n'})
