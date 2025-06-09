import sys
import importlib
from pathlib import Path
from types import ModuleType
from datetime import datetime
from zoneinfo import ZoneInfo

root = Path(__file__).resolve().parents[1]
sys.path.append(str(root))
sys.path.append(str(root / 'src'))


def _load(monkeypatch):
    st = ModuleType('streamlit')
    st.session_state = {}
    monkeypatch.setitem(sys.modules, 'streamlit', st)
    mod = importlib.reload(importlib.import_module('src.utils.time_utils'))
    return st, mod


def test_format_user_tz_basic(monkeypatch):
    st, mod = _load(monkeypatch)
    st.session_state['userTZ'] = 'America/New_York'
    dt = datetime(2024, 1, 1, 12, 0, tzinfo=ZoneInfo('UTC'))
    assert mod.format_user_tz(dt) == dt.astimezone(ZoneInfo('America/New_York')).strftime('%Y-%m-%d %H:%M')


def test_format_user_tz_invalid_string(monkeypatch):
    st, mod = _load(monkeypatch)
    st.session_state['userTZ'] = 'UTC'
    assert mod.format_user_tz('bad') == 'bad'
