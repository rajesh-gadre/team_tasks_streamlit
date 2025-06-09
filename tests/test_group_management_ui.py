import sys
from types import ModuleType, SimpleNamespace
from pathlib import Path

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
st.header = lambda *a, **k: None
st.dataframe = lambda *a, **k: None
st.form = lambda *a, **k: SimpleNamespace(__enter__=lambda self: None, __exit__=lambda self, exc_type, exc, tb: None)
st.selectbox = lambda *a, **k: ''
st.text_input = lambda *a, **k: ''
st.form_submit_button = lambda *a, **k: False
st.success = lambda *a, **k: None
st.rerun = lambda: None
sys.modules['streamlit'] = st
import importlib
import src.ui.group_management as gm
importlib.reload(gm)

def test_render_group_management_tabs(monkeypatch):
    monkeypatch.setattr(gm, 'get_group_service', lambda: SimpleNamespace(get_groups=lambda: []))
    monkeypatch.setattr(gm, 'get_user_group_service', lambda: SimpleNamespace(get_user_groups=lambda: []))
    tabs_called.clear()
    gm.render_group_management()
    assert tabs_called and tabs_called[0] == ['Groups', 'UserGroups']
