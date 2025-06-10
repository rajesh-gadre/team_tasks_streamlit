import sys
from types import ModuleType, SimpleNamespace
from pathlib import Path

root = Path(__file__).resolve().parents[1]
sys.path.append(str(root))
sys.path.append(str(root / 'src'))

st = ModuleType('streamlit')
captured = {}
st.header = lambda *a, **k: None
st.button = lambda *a, **k: False
st.rerun = lambda: None
st.write = lambda msg, *a, **k: captured.setdefault('msg', msg)
class SessionState(dict):
    def __getattr__(self, name):
        return self.get(name)
    def __setattr__(self, name, value):
        self[name] = value
st.session_state = SessionState({'user': {'email': 'u'}, 'userId': 'u'})
sys.modules['streamlit'] = st

import importlib
import src.ui.task_list as tl
import src.ui.group_tasks as gt
importlib.reload(tl)
importlib.reload(gt)


def test_render_group_tasks_count(monkeypatch):
    data = [('G', SimpleNamespace())] * 3
    monkeypatch.setattr(gt, '_get_group_tasks', lambda status: data)
    monkeypatch.setattr(gt, '_render_group_task_list', lambda *a, **k: None)
    captured.clear()
    gt.render_group_tasks(gt.TaskStatus.ACTIVE)
    assert captured['msg'] == 'Total tasks: 3'
