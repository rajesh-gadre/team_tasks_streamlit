import sys
from pathlib import Path
from types import ModuleType, SimpleNamespace
root = Path(__file__).resolve().parents[1]
sys.path.append(str(root))
sys.path.append(str(root / 'src'))
st = ModuleType('streamlit')
st.session_state = {}
expander_called = []

def expander(*a, **k):
    expander_called.append(a)

    class C:

        def __enter__(self):
            return self

        def __exit__(self, exc_type, exc, tb):
            pass
    return C()

class Tab:

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        pass
tabs_called = []

def tabs(names):
    tabs_called.append(names)
    return [Tab() for _ in names]
st.expander = expander
st.tabs = tabs
st.header = lambda *a, **k: None
st.json = lambda *a, **k: None
st.dataframe = lambda *a, **k: None
st.number_input = lambda *a, **k: 1
st.button = lambda *a, **k: True
st.checkbox = lambda *a, **k: True
sys.modules['streamlit'] = st
pd = ModuleType('pandas')
pd.DataFrame = lambda data=None: data
sys.modules['pandas'] = pd
import src.ui.navigation as navigation

def test_debug_page_tabs_and_delete(monkeypatch):
    tabs_called.clear()
    expander_called.clear()
    monkeypatch.setattr('src.ui.navigation.get_all_chats', lambda: [])
    monkeypatch.setattr('src.ui.navigation.get_task_service', lambda: SimpleNamespace(get_all_tasks=lambda: []))
    monkeypatch.setattr('src.ui.navigation.get_prompt_repository', lambda: SimpleNamespace(get_all_prompts=lambda: []))
    monkeypatch.setattr('src.ui.navigation.get_eval_inputs', lambda: [])
    monkeypatch.setattr('src.ui.navigation.get_eval_results', lambda: [])
    delete_calls = []
    monkeypatch.setattr('src.ui.navigation.delete_all_chats_one_by_one', lambda count: delete_calls.append(count))
    monkeypatch.setattr(st, 'button', lambda *a, **k: True)
    st.checkbox = lambda *a, **k: True
    navigation.debug_page()
    assert tabs_called
    assert not expander_called
    assert delete_calls == [1]
    st.checkbox = lambda *a, **k: False
    navigation.debug_page()
    assert delete_calls == [1]
