import sys
from pathlib import Path
from types import ModuleType

root = Path(__file__).resolve().parents[1]
sys.path.append(str(root))
sys.path.append(str(root / 'src'))

st = ModuleType('streamlit')

class Tab:
    def __enter__(self):
        return self
    def __exit__(self, exc_type, exc, tb):
        pass

tabs_called = []

def tabs(names):
    tabs_called.append(names)
    return [Tab() for _ in names]

st.tabs = tabs
st.title = lambda *a, **k: None
st.session_state = {}

sys.modules['streamlit'] = st

import importlib
import src.ui.tasks_page as tasks_page
importlib.reload(tasks_page)


def test_render_my_tasks_page(monkeypatch):
    monkeypatch.setattr(tasks_page, 'render_active_tasks', lambda: None)
    monkeypatch.setattr(tasks_page, 'render_completed_tasks', lambda: None)
    monkeypatch.setattr(tasks_page, 'render_deleted_tasks', lambda: None)
    monkeypatch.setattr(tasks_page, 'render_task_form', lambda *a, **k: None)
    tabs_called.clear()
    tasks_page.render_my_tasks_page()
    assert tabs_called and tabs_called[0] == ['Active Tasks', 'Completed Tasks', 'Deleted Tasks']


def test_render_group_tasks_page(monkeypatch):
    monkeypatch.setattr(tasks_page, 'render_group_active_tasks', lambda: None)
    monkeypatch.setattr(tasks_page, 'render_group_completed_tasks', lambda: None)
    monkeypatch.setattr(tasks_page, 'render_group_deleted_tasks', lambda: None)
    tabs_called.clear()
    tasks_page.render_group_tasks_page()
    assert tabs_called and tabs_called[0] == ['Active Tasks', 'Completed Tasks', 'Deleted Tasks']
