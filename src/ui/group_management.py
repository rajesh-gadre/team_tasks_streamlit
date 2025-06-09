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
    action = st.radio('Action', ['Add new record', 'Modify existing record'])
    if action == 'Add new record':
        group_name = st.text_input('Group Name')
        user_email = st.text_input('User Email')
        if st.button('Add'):
            data = {'groupName': group_name, 'userEmail': user_email, 'status': 'active'}
            service.create_user_group(data)
            st.success('Saved')
            st.rerun()
    else:
        options = [''] + [r['id'] for r in records]
        record_id = st.selectbox('RecordId', options)
        record = next((r for r in records if r['id'] == record_id), {}) if record_id else {}
        group_name = st.text_input('Group Name', value=record.get('groupName', ''))
        user_email = st.text_input('User Email', value=record.get('userEmail', ''))
        cols = st.columns(2)
        if cols[0].button('Update') and record_id:
            data = {'groupName': group_name, 'userEmail': user_email}
            service.update_user_group(record_id, data)
            st.success('Saved')
            st.rerun()
        if cols[1].button('Delete') and record_id:
            service.delete_user_group(record_id)
            st.success('Deleted')
            st.rerun()


def render_group_management():
    st.header('Group Management')
    tabs = st.tabs(['Groups', 'UserGroups'])
    with tabs[0]:
        _groups_tab()
    with tabs[1]:
        _user_groups_tab()
