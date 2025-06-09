import sys
from pathlib import Path
from types import ModuleType, SimpleNamespace

root = Path(__file__).resolve().parents[1]
sys.path.append(str(root))
sys.path.append(str(root / 'src'))

st = ModuleType('streamlit')

class SessionState(dict):
    def __getattr__(self, name):
        return self.get(name)

    def __setattr__(self, name, value):
        self[name] = value

st.session_state = SessionState({'userId': 'u1', 'user': {'name': 'N', 'email': 'E'}, 'userTZ': 'America/Los_Angeles'})
st.header = lambda *a, **k: None
st.write = lambda *a, **k: None
st.selectbox = lambda *a, **k: 'UTC'
st.button = lambda *a, **k: True
st.success = lambda *a, **k: None
sys.modules['streamlit'] = st

import importlib
import src.ui.settings as settings
importlib.reload(settings)


def test_render_settings(monkeypatch):
    calls = {}
    monkeypatch.setattr(settings, 'get_user_group_service', lambda: SimpleNamespace(get_groups_for_user=lambda uid: [{'groupName': 'G'}]))
    monkeypatch.setattr(settings, 'get_user_service', lambda: SimpleNamespace(update_timezone=lambda uid, tz: calls.setdefault('update', (uid, tz)) or True))
    settings.render_settings()
    assert calls['update'][1] == 'UTC'

