import sys
from pathlib import Path
from types import ModuleType

root = Path(__file__).resolve().parents[1]
sys.path.append(str(root))
sys.path.append(str(root / 'src'))

st = ModuleType('streamlit')
st.write = lambda *a, **k: None

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
st.title = lambda *a, **k: None
sys.modules['streamlit'] = st

import importlib
import src.ui.evals_page as ep
importlib.reload(ep)


def test_render_evals(monkeypatch):
    calls = []
    monkeypatch.setattr(ep, 'render_eval_candidates', lambda: calls.append('c'))
    monkeypatch.setattr(ep, 'render_run_evals', lambda: calls.append('r'))
    tabs_called.clear()
    ep.render_evals()
    assert tabs_called and tabs_called[0] == ['Eval Candidates', 'Run Evals']
    assert calls == ['c', 'r']
