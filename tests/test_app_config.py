import sys
from pathlib import Path
from types import ModuleType, SimpleNamespace
root = Path(__file__).resolve().parents[1]
sys.path.append(str(root))

st = ModuleType('streamlit')
st.session_state = {}
st.secrets = {}
st.set_page_config = lambda *a, **k: None
st.query_params = SimpleNamespace(to_dict=lambda: {})
st.markdown = lambda *a, **k: None
sys.modules['streamlit'] = st

auth_mod = ModuleType('aiclub_auth_lib.oauth')
class Dummy:
    def __init__(self, config):
        self.config = config
auth_mod.AIClubGoogleAuth = Dummy
sys.modules['aiclub_auth_lib.oauth'] = auth_mod

dotenv = ModuleType('dotenv')
dotenv.load_dotenv = lambda *a, **k: None
sys.modules['dotenv'] = dotenv

pd = ModuleType('pandas')
pd.DataFrame = lambda *a, **k: None
sys.modules['pandas'] = pd

google = ModuleType('google')
cloud = ModuleType('cloud')
firestore = ModuleType('firestore_v1')
firestore.FieldFilter = object
sys.modules['google'] = google
sys.modules['google.cloud'] = cloud
sys.modules['google.cloud.firestore_v1'] = firestore

from src.app_config import build_auth_config

def test_build_auth_config(monkeypatch):
    monkeypatch.setenv('AUTH_TYPE', 'google')
    monkeypatch.setenv('GOOGLE_CLIENT_ID', 'cid')
    monkeypatch.setenv('GOOGLE_CLIENT_SECRET', 'sec')
    monkeypatch.setenv('GOOGLE_REDIRECT_URI', 'uri')
    monkeypatch.setenv('AUTH0_DOMAIN', 'd')
    monkeypatch.setenv('AUTH0_CLIENT_ID', 'aid')
    monkeypatch.setenv('AUTH0_CLIENT_SECRET', 'asec')
    monkeypatch.setenv('AUTH0_CALLBACK_URL', 'aurl')
    cfg = build_auth_config('auth0')
    assert cfg['domain'] == 'd'
    assert cfg['client_id'] == 'aid'
    assert cfg['client_secret'] == 'asec'
    assert cfg['redirect_uri'] == 'aurl'
