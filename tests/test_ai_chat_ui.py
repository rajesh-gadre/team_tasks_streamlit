import sys
from pathlib import Path
from types import ModuleType, SimpleNamespace

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
st.markdown = lambda *a, **k: None
st.form = lambda *a, **k: Tab()
st.text_area = lambda *a, **k: ''
st.form_submit_button = lambda *a, **k: False

class SessionState(dict):
    def __getattr__(self, name):
        return self.get(name)

    def __setattr__(self, name, value):
        self[name] = value

st.session_state = SessionState({'user': {'email': 'e'}})
st.code = lambda *a, **k: None
st.json = lambda *a, **k: None
st.info = lambda *a, **k: None
st.button = lambda *a, **k: False
st.rerun = lambda: None
sys.modules['streamlit'] = st

import importlib
import src.ui.ai_chat as ai_chat
importlib.reload(ai_chat)


def test_render_ai_chat_tabs(monkeypatch):
    monkeypatch.setattr(ai_chat, 'get_client', lambda: SimpleNamespace(query=lambda *a, **k: []))
    tabs_called.clear()
    ai_chat.render_ai_chat()
    assert tabs_called and tabs_called[0] == ['Main', 'Feedback']
