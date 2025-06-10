import sys
from types import ModuleType, SimpleNamespace
from pathlib import Path

root = Path(__file__).resolve().parents[1]
sys.path.append(str(root))
sys.path.append(str(root / 'src'))

st = ModuleType('streamlit')
class Expander:
    def __enter__(self):
        return self
    def __exit__(self, exc_type, exc, tb):
        pass
st.expander = lambda *a, **k: Expander()
class SessionState(dict):
    def __getattr__(self, name):
        return self.get(name)

    def __setattr__(self, name, value):
        self[name] = value

st.session_state = SessionState({'user': {'email': 'u'}})
class Col:
    def __init__(self):
        self.is_details = False

    def write(self, *a, **k):
        pass

    def button(self, *a, **k):
        return self.is_details

    def columns(self, n):
        return [Col() for _ in range(n)]

def columns(spec):
    cols = [Col() for _ in range(len(spec))]
    if cols:
        cols[-1].is_details = True
    return cols

st.columns = columns
class Container:
    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        pass

st.container = lambda: Container()
st.markdown = lambda *a, **k: None
st.header = lambda *a, **k: None
st.info = lambda *a, **k: None
st.selectbox = lambda *a, **k: 'Title'
st.checkbox = lambda *a, **k: False
st.json = lambda *a, **k: None
btn_calls = {}

def button(label, key=None, help=None):
    if 'details' in key:
        btn_calls['clicked'] = True
        return True
    return False
st.button = button
class Col:
    def __init__(self):
        self.is_details = False

    def write(self, *a, **k):
        pass

    def button(self, *a, **k):
        return self.is_details

    def columns(self, n):
        return [Col() for _ in range(n)]

def columns(spec):
    cols = [Col() for _ in range(len(spec))]
    if cols:
        cols[-1].is_details = True
    return cols

st.columns = columns
st.rerun = lambda: None
sys.modules['streamlit'] = st

import importlib
import src.ui.task_list as tl
importlib.reload(tl)

def test_details_fetch(monkeypatch):
    task_obj = SimpleNamespace(id='1', title='A', user_id='u', status='active', due_date=None, description='d', notes='n', updates=[])
    calls = {}
    def _get(u, i):
        calls['get'] = (u, i)
        return task_obj

    service = SimpleNamespace(
        complete_task=lambda u, i: False,
        delete_task=lambda u, i: False,
        restore_task=lambda u, i: False,
        get_task=_get,
    )
    monkeypatch.setattr(tl, 'get_task_service', lambda: service)
    tl.render_task_list([task_obj], tl.TaskStatus.ACTIVE)
    assert calls.get('get') == ('u', '1')
