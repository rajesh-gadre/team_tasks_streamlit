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
st.radio = lambda *a, **k: ''
st.columns = lambda n: [SimpleNamespace(button=lambda *a, **k: False) for _ in range(n)]
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


def test_user_groups_add(monkeypatch):
    calls = {}
    service = SimpleNamespace(get_user_groups=lambda: [], create_user_group=lambda data: calls.setdefault('create', data))
    monkeypatch.setattr(gm, 'get_user_group_service', lambda: service)
    st.radio = lambda *a, **k: 'Add new record'
    st.button = lambda label: label == 'Add'
    st.text_input = lambda *a, **k: 'v'
    gm._user_groups_tab()
    assert calls['create'] == {'groupName': 'v', 'userEmail': 'v', 'status': 'active'}


def test_user_groups_delete(monkeypatch):
    record = {'id': '1', 'groupName': 'a', 'userEmail': 'e'}
    calls = []
    service = SimpleNamespace(get_user_groups=lambda: [record], update_user_group=lambda *a, **k: None, delete_user_group=lambda rid: calls.append(('delete', rid)))
    monkeypatch.setattr(gm, 'get_user_group_service', lambda: service)
    st.radio = lambda *a, **k: 'Modify existing record'
    st.selectbox = lambda *a, **k: '1'
    st.text_input = lambda label, value='': value
    class Col:
        def __init__(self, flag):
            self.flag = flag
        def button(self, label):
            return label == 'Delete' and self.flag
    st.columns = lambda n: [Col(False), Col(True)]
    gm._user_groups_tab()
    assert calls == [('delete', '1')]
