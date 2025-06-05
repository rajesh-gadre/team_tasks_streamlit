import sys
from pathlib import Path
from unittest.mock import MagicMock

sys.path.append(str(Path(__file__).resolve().parents[1]))

from tasks.task_service import TaskService


def _setup_service(monkeypatch):
    mock_repo = MagicMock()
    monkeypatch.setattr('tasks.task_service.get_task_repository', lambda: mock_repo)
    service = TaskService()
    return service, mock_repo


def test_create_task(monkeypatch):
    service, repo = _setup_service(monkeypatch)
    repo.create_task.return_value = 'tid'
    data = {
        'title': 'Test',
        'description': 'desc',
        'notes': 'n',
        'due_date': '2024-01-01',
    }
    result = service.create_task('u1', data)
    assert result == 'tid'
    repo.create_task.assert_called_once()
    created = repo.create_task.call_args.args[0]
    assert created.user_id == 'u1'
    assert created.title == 'Test'
    assert created.description == 'desc'
    assert created.notes == 'n'


def test_update_task(monkeypatch):
    service, repo = _setup_service(monkeypatch)
    service.update_task('u1', 't1', {'title': 'new', 'due_date': '2024-01-02'})
    repo.update_task.assert_called_once_with('u1', 't1', {'title': 'new', 'dueDate': '2024-01-02'})


def test_delete_restore_complete(monkeypatch):
    service, repo = _setup_service(monkeypatch)
    service.delete_task('u1', 't1')
    repo.delete_task.assert_called_once_with('u1', 't1')
    service.restore_task('u1', 't1')
    repo.restore_task.assert_called_once_with('u1', 't1')
    service.complete_task('u1', 't1')
    repo.complete_task.assert_called_once_with('u1', 't1')
