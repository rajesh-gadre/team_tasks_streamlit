import sys
from types import ModuleType, SimpleNamespace
from pathlib import Path

root = Path(__file__).resolve().parents[1]
sys.path.append(str(root))
sys.path.append(str(root / 'src'))

st = ModuleType('streamlit')
st.header = lambda *a, **k: None
st.write = lambda *a, **k: None
captured = {}
def _multiselect(label, opts):
    captured['opts'] = opts
    return [opts[0]] if opts else []
st.multiselect = _multiselect
st.selectbox = lambda label, opts: opts[1] if len(opts) > 1 else ''
st.button = lambda *a, **k: True
st.success = lambda *a, **k: setattr(st, 'status', 'success')
st.error = lambda *a, **k: setattr(st, 'status', 'error')
st.session_state = {}
sys.modules['streamlit'] = st

import importlib
import src.ui.task_assignment as ta
importlib.reload(ta)


def test_render_task_assignment(monkeypatch):
    tasks = [
        SimpleNamespace(id='1', title='A', user_id='u1', status='active'),
        SimpleNamespace(id='2', title='B', user_id='u1', status='completed'),
    ]
    users = [{'userId': 'u2', 'userEmail': 'e'}]
    service = SimpleNamespace(get_all_tasks=lambda: tasks, assign_tasks=lambda ids, uid: setattr(st, 'assigned', (ids, uid)))
    monkeypatch.setattr(ta, 'get_task_service', lambda: service)
    monkeypatch.setattr(ta, 'get_user_service', lambda: SimpleNamespace(get_users=lambda: users))
    ta.render_task_assignment()
    assert getattr(st, 'assigned', None) == (['1'], 'u2')
    assert captured['opts'] == ["A (u1)"]
