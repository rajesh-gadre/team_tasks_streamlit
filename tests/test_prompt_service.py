import sys
from pathlib import Path
from unittest.mock import MagicMock

sys.path.append(str(Path(__file__).resolve().parents[1]))

from ai.prompt_service import PromptService


def _setup(monkeypatch):
    repo = MagicMock()
    monkeypatch.setattr('ai.prompt_service.get_prompt_repository', lambda: repo)
    service = PromptService()
    return service, repo


def test_get_all_prompts(monkeypatch):
    service, repo = _setup(monkeypatch)
    repo.get_latest_prompts.return_value = ['p']
    result = service.get_all_prompts()
    assert result == ['p']
    repo.get_latest_prompts.assert_called_once()


def test_update_prompt_creates_new_version(monkeypatch):
    service, repo = _setup(monkeypatch)
    repo.create_prompt_version.return_value = 'new'
    result = service.update_prompt('id1', {'text': 'new text'})
    assert result is True
    repo.create_prompt_version.assert_called_once_with('id1', {'text': 'new text'})

