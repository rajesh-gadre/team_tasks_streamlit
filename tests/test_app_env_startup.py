import sys
import os
from pathlib import Path
from types import ModuleType, SimpleNamespace

class Bag(dict):
    def __getattr__(self, name):
        return self.get(name)
    def __setattr__(self, name, value):
        self[name] = value

root = Path(__file__).resolve().parents[1]
sys.path.append(str(root))

st = ModuleType('streamlit')
st.session_state = Bag()
st.query_params = SimpleNamespace(to_dict=lambda: {})
st.set_page_config = lambda *a, **k: None
st.markdown = lambda *a, **k: None
sys.modules['streamlit'] = st

auth_mod = ModuleType('aiclub_auth_lib.oauth')
class Dummy:
    def __init__(self, config):
        self.config = config
auth_mod.AIClubGoogleAuth = Dummy
sys.modules['aiclub_auth_lib.oauth'] = auth_mod

auth0_mod = ModuleType('src.auth.auth0_auth')
class Dummy0:
    def __init__(self, config):
        self.config = config
auth0_mod.Auth0Auth = Dummy0
sys.modules['src.auth.auth0_auth'] = auth0_mod

session_mod = ModuleType('src.auth.session')
session_mod.init_session = lambda: None
session_mod.login_user = lambda *a, **k: None
session_mod.logout_user = lambda *a, **k: None
sys.modules['src.auth.session'] = session_mod

ui_mod = ModuleType('src.ui.navigation')
ui_mod.render_login_page = lambda *a, **k: None
ui_mod.render_main_page = lambda *a, **k: None
ui_mod.render_sidebar = lambda *a, **k: None
sys.modules['src.ui.navigation'] = ui_mod

dotenv = ModuleType('dotenv')
dotenv.load_dotenv = lambda *a, **k: None
sys.modules['dotenv'] = dotenv

os.environ['AUTH_TYPE'] = 'google'
os.environ['GOOGLE_CLIENT_ID'] = 'cid'
os.environ['GOOGLE_CLIENT_SECRET'] = 'sec'
os.environ['GOOGLE_REDIRECT_URI'] = 'uri'

app = __import__('app')


def test_app_uses_env_vars():
    assert isinstance(app.auth.config, dict)
    assert app.auth.config['client_id'] == 'cid'
