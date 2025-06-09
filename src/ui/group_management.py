import streamlit as st
from src.groups.group_service import get_group_service
from src.groups.user_group_service import get_user_group_service


def _groups_tab():
    service = get_group_service()
    groups = service.get_groups()
    st.dataframe(groups)

    st.subheader("Create New Group")
    new_group_name = st.text_input('Group Name', key='new_group_name_input')
    if st.button('Create Group'):
        if new_group_name:
            service.create_group(new_group_name)
            st.success('Group created')
            st.rerun()

    st.subheader("Modify Group Name")
    group_options = [''] + [g['groupName'] for g in groups]
    selected_group_name = st.selectbox('Select Group Name', group_options, key='modify_group_select')

    if selected_group_name:
        selected_group = next((g for g in groups if g['groupName'] == selected_group_name), {})
        updated_name = st.text_input('New Name', value=selected_group.get('groupName', ''), key='modify_group_name_input')
        if st.button('Update Group'):
            service.update_group(selected_group['id'], updated_name)
            st.success('Group updated')
            st.rerun()


def _user_groups_tab():
    service = get_user_group_service()
    records = service.get_user_groups()
    st.dataframe(records)
    action = st.radio('Action', ['Add new record', 'Modify existing record'])
    if action == 'Add new record':
        group_name = st.text_input('Group Name', key='add_group_name')
        user_email = st.text_input('User Email', key='add_user_email')
        if st.button('Add'):
            data = {'groupName': group_name, 'userEmail': user_email, 'status': 'active'}
            service.create_user_group(data)
            st.success('Saved')
            st.rerun()
    else:
        options = [''] + [r['id'] for r in records]
        record_id = st.selectbox('RecordId', options)
        record = next((r for r in records if r['id'] == record_id), {}) if record_id else {}
        group_name = st.text_input('Group Name', value=record.get('groupName', ''), key='modify_group_name')
        user_email = st.text_input('User Email', value=record.get('userEmail', ''), key='modify_user_email')
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
