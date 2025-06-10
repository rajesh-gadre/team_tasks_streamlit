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
sys.modules['streamlit'] = st

import importlib
import src.ui.system_management as sm
importlib.reload(sm)


def test_render_system_management(monkeypatch):
    calls = []
    monkeypatch.setattr(sm, 'render_prompt_management', lambda: calls.append('p'))
    monkeypatch.setattr(sm, 'render_group_management', lambda: calls.append('g'))
    monkeypatch.setattr(sm, 'render_task_assignment', lambda: calls.append('t'))
    tabs_called.clear()
    sm.render_system_management()
    assert tabs_called and tabs_called[0] == ['Prompt Management', 'Group Management', 'Assign Tasks']
    assert calls == ['p', 'g', 't']
