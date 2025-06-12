import sys
from pathlib import Path
from types import ModuleType, SimpleNamespace

root = Path(__file__).resolve().parents[1]
sys.path.append(str(root))
sys.path.append(str(root / 'src'))

st = ModuleType('streamlit')
record = {}

class Form:
    def __enter__(self):
        return None
    def __exit__(self, exc_type, exc, tb):
        pass

st.form = lambda **k: Form()
st.form_submit_button = lambda label: False
st.text_area = lambda label, value='': value
st.subheader = lambda *a, **k: None
st.selectbox = lambda *a, **k: ''
st.download_button = lambda label, data, file_name: record.update({'data': data, 'file_name': file_name})
st.file_uploader = lambda *a, **k: None
st.button = lambda *a, **k: False
st.error = lambda *a, **k: record.update({'error': True})
st.success = lambda *a, **k: record.update({'success': True})
st.rerun = lambda: record.update({'rerun': True})
st.header = lambda *a, **k: None
st.info = lambda *a, **k: None
sys.modules['streamlit'] = st

import importlib
import src.ui.prompt_management as pm
importlib.reload(pm)


def test_download_section():
    record.clear()
    active = SimpleNamespace(text='x', version=3)
    pm._download_section('p', active)
    assert record == {'data': 'x', 'file_name': 'p_v3.txt'}


def test_save_prompt(monkeypatch):
    record.clear()
    service = SimpleNamespace(update_prompt=lambda *a, **k: True)
    monkeypatch.setattr(pm, 'get_prompt_service', lambda: service)
    pm._save_prompt('text', 'id1')
    assert record.get('success') and record.get('rerun')


def test_save_prompt_invalid(monkeypatch):
    record.clear()
    service = SimpleNamespace(update_prompt=lambda *a, **k: True)
    monkeypatch.setattr(pm, 'get_prompt_service', lambda: service)
    pm._save_prompt(' ', 'id1')
    assert record.get('error')
