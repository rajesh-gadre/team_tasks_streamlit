import sys
from types import ModuleType, SimpleNamespace
from pathlib import Path

root = Path(__file__).resolve().parents[1]
sys.path.append(str(root))
sys.path.append(str(root / 'src'))

st = ModuleType('streamlit')
st.write = lambda *a, **k: None
class SessionState(dict):
    def __getattr__(self, name):
        return self.get(name)

    def __setattr__(self, name, value):
        self[name] = value
st.session_state = SessionState()
output = {}

class Spinner:
    def __enter__(self):
        return None
    def __exit__(self, exc_type, exc, tb):
        pass

st.header = lambda *a, **k: None
st.button = lambda *a, **k: True
st.spinner = lambda *a, **k: Spinner()
st.code = lambda text: output.update({'code': text})
st.success = lambda *a, **k: output.update({'status': 'success'})
st.error = lambda *a, **k: output.update({'status': 'error'})
st.rerun = lambda: None
sys.modules['streamlit'] = st

import importlib
import src.ui.run_tests as run_tests

def test_render_run_tests(monkeypatch):
    st.session_state = SessionState()
    sys.modules['streamlit'] = st
    importlib.reload(run_tests)
    st.button = lambda *a, **k: True
    st.spinner = lambda *a, **k: Spinner()
    def fake_run(*a, **k):
        return SimpleNamespace(stdout='ok', stderr='', returncode=0)
    monkeypatch.setattr(run_tests.subprocess, 'run', fake_run)
    run_tests.render_run_tests()
    assert st.session_state.test_output == 'ok'
    assert output['status'] == 'success'
    assert output['code'] == 'ok'
