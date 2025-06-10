import streamlit as st
from zoneinfo import available_timezones
from src.users.user_service import get_user_service
from src.groups.user_group_service import get_user_group_service
from src.ui.changelog import render_changelog
from src.ui.run_tests import render_run_tests

def _user_settings_tab():
    user = st.session_state.user or {}
    st.write(f"Name: {user.get('name','')}")
    st.write(f"Email: {user.get('email','')}")
    groups = get_user_group_service().get_groups_for_user(st.session_state.userId)
    group_names = ', '.join(g.get('groupName','') for g in groups)
    st.write(f"Groups: {group_names}")
    options = sorted(available_timezones())
    current = st.session_state.get('userTZ','America/Los_Angeles')
    value = st.selectbox('Timezone', options, index=options.index(current) if current in options else 0)
    if st.button('Save'):
        if get_user_service().update_timezone(st.session_state.userId, value):
            st.session_state.userTZ = value
            st.success('Saved')

def render_settings():
    st.title('Settings')
    tabs = st.tabs(['Settings', 'ChangeLog', 'Run Tests'])
    with tabs[0]:
        _user_settings_tab()
    with tabs[1]:
        render_changelog()
    with tabs[2]:
        render_run_tests()
