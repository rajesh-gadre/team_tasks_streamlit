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
st.subheader = lambda *a, **k: None
st.divider = lambda *a, **k: None
st.text_input = lambda *a, **k: ''
st.selectbox = lambda *a, **k: ''
st.button = lambda *a, **k: False
st.success = lambda *a, **k: None
st.rerun = lambda: None
sys.modules['streamlit'] = st

import importlib
import src.ui.group_management as gm
importlib.reload(gm)


def test_render_group_management_tabs(monkeypatch):
    monkeypatch.setattr(gm, 'get_group_service', lambda: SimpleNamespace(get_groups=lambda: []))
    monkeypatch.setattr(gm, 'get_user_group_service', lambda: SimpleNamespace(get_user_groups=lambda: []))
    monkeypatch.setattr(gm, 'get_user_service', lambda: SimpleNamespace(get_users=lambda: []))
    tabs_called.clear()
    gm.render_group_management()
    assert tabs_called and tabs_called[0] == ['Groups', 'UserGroups']


def test_user_groups_add(monkeypatch):
    calls = {}
    ug_service = SimpleNamespace(get_user_groups=lambda: [], create_user_group=lambda d: calls.setdefault('create', d))
    group_service = SimpleNamespace(get_groups=lambda: [{'id': 'g1', 'groupName': 'G'}])
    user_service = SimpleNamespace(get_users=lambda: [{'userId': 'u1', 'userEmail': 'E'}])
    monkeypatch.setattr(gm, 'get_user_group_service', lambda: ug_service)
    monkeypatch.setattr(gm, 'get_group_service', lambda: group_service)
    monkeypatch.setattr(gm, 'get_user_service', lambda: user_service)
    values = ['G', 'E', '']
    st.selectbox = lambda *a, **k: values.pop(0)
    st.button = lambda label: label == 'Add User to Group'
    gm._user_groups_tab()
    assert calls['create'] == {
        'groupId': 'g1',
        'groupName': 'G',
        'userId': 'u1',
        'userEmail': 'E',
        'status': 'active'
    }


def test_user_groups_delete(monkeypatch):
    record = {'id': '1', 'groupId': 'g1', 'groupName': 'G', 'userId': 'u1', 'userEmail': 'E'}
    calls = []
    ug_service = SimpleNamespace(get_user_groups=lambda: [record], delete_user_group=lambda rid: calls.append(('delete', rid)))
    group_service = SimpleNamespace(get_groups=lambda: [{'id': 'g1', 'groupName': 'G'}])
    user_service = SimpleNamespace(get_users=lambda: [{'userId': 'u1', 'userEmail': 'E'}])
    monkeypatch.setattr(gm, 'get_user_group_service', lambda: ug_service)
    monkeypatch.setattr(gm, 'get_group_service', lambda: group_service)
    monkeypatch.setattr(gm, 'get_user_service', lambda: user_service)
    values = ['', '', 'G', 'E']
    st.selectbox = lambda *a, **k: values.pop(0)
    st.button = lambda label: label == 'Delete?'
    gm._user_groups_tab()
    assert calls == [('delete', '1')]
