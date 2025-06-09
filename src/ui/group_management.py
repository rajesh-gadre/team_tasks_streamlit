import streamlit as st
from src.groups.group_service import get_group_service
from src.groups.user_group_service import get_user_group_service


def _groups_tab():
    service = get_group_service()
    groups = service.get_groups()
    st.dataframe(groups)
    options = [''] + [g['id'] for g in groups]
    group_id = st.selectbox('Group', options)
    name = st.text_input('Group Name')
    if st.button('Save Group'):
        if group_id:
            service.update_group(group_id, name)
        else:
            service.create_group(name)
        st.success('Saved')
        st.rerun()


def _user_groups_tab():
    service = get_user_group_service()
    records = service.get_user_groups()
    st.dataframe(records)
    options = [''] + [r['id'] for r in records]
    record_id = st.selectbox('Record', options)
    group_id = st.text_input('GroupId')
    group_name = st.text_input('GroupName')
    user_id = st.text_input('UserId')
    user_name = st.text_input('UserName')
    user_email = st.text_input('UserEmail')
    if st.button('Save UserGroup'):
        data = {'groupId': group_id, 'groupName': group_name, 'userId': user_id, 'userName': user_name, 'userEmail': user_email}
        if record_id:
            service.update_user_group(record_id, data)
        else:
            service.create_user_group(data)
        st.success('Saved')
        st.rerun()


def render_group_management():
    st.header('Group Management')
    tabs = st.tabs(['Groups', 'UserGroups'])
    with tabs[0]:
        _groups_tab()
    with tabs[1]:
        _user_groups_tab()
