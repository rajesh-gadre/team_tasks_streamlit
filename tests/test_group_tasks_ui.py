import sys
from pathlib import Path
from types import ModuleType, SimpleNamespace

root = Path(__file__).resolve().parents[1]
sys.path.append(str(root))
sys.path.append(str(root / 'src'))

st = ModuleType('streamlit')
st.header = lambda *a, **k: None
captured = []
st.write = lambda s: captured.append(s)
st.selectbox = lambda label, opts: opts[1] if len(opts) > 1 else ''

class SessionState(dict):
    def __getattr__(self, name):
        return self.get(name)

    def __setattr__(self, name, value):
        self[name] = value

st.session_state = SessionState({'userId': 'u'})
sys.modules['streamlit'] = st

import importlib
import src.ui.group_tasks as gt
importlib.reload(gt)


def test_render_group_tasks(monkeypatch):
    tasks = [
        SimpleNamespace(title='A', user_id='a', status='active', updated_at=1, created_at=1),
        SimpleNamespace(title='B', user_id='b', status='completed', updated_at=2, created_at=2),
    ]
    ug_service = SimpleNamespace(
        get_groups_for_user=lambda uid: [{'groupName': 'G'}],
        get_user_groups=lambda: [{'groupName': 'G', 'userEmail': 'a'}, {'groupName': 'G', 'userEmail': 'b'}],
    )
    monkeypatch.setattr(gt, 'get_user_group_service', lambda: ug_service)
    monkeypatch.setattr(gt, 'get_task_service', lambda: SimpleNamespace(get_all_tasks=lambda: tasks))
    captured.clear()
    gt.render_group_tasks()
    assert captured == ['B - b - completed', 'A - a - active']
