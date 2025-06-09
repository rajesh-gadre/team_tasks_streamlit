import streamlit as st
from src.groups.group_service import get_group_service
from src.groups.user_group_service import get_user_group_service
from src.users.user_service import get_user_service


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
    group_service = get_group_service()
    user_service = get_user_service()
    records = service.get_user_groups()
    groups = group_service.get_groups()
    users = user_service.get_users()
    st.dataframe(records)

    st.subheader('Add User to Group')
    group_options = [''] + [g['groupName'] for g in groups]
    add_group = st.selectbox('Group', group_options, key='add_group')
    user_options = [''] + [u.get('userName') or u['userEmail'] for u in users]
    add_user_label = st.selectbox('User', user_options, key='add_user')
    if st.button('Add User to Group'):
        group = next((g for g in groups if g['groupName'] == add_group), None)
        user = next((u for u in users if (u.get('userName') or u['userEmail']) == add_user_label), None)
        if group and user:
            exists = any(
                ((r.get('groupId') == group.get('id') or r.get('groupName') == group['groupName']) and
                 (r.get('userId') == user.get('userId') or r.get('userEmail') == user['userEmail']) and
                 r.get('status') != 'deleted')
                for r in records
            )
            if not exists:
                data = {
                    'groupId': group.get('id'),
                    'groupName': group.get('groupName'),
                    'userId': user.get('userId'),
                    'userEmail': user['userEmail'],
                    'status': 'active',
                }
                if 'userName' in user:
                    data['userName'] = user['userName']
                service.create_user_group(data)
                st.success('Saved')
                st.rerun()

    st.divider()
    st.subheader('Remove User from Group')
    remove_group_name = st.selectbox('Group', group_options, key='remove_group')
    group = next((g for g in groups if g['groupName'] == remove_group_name), None)
    if group:
        group_records = [r for r in records if (r.get('groupId') == group.get('id') or r.get('groupName') == group['groupName']) and r.get('status') != 'deleted']
        user_opts = [''] + [r.get('userEmail') for r in group_records]
        remove_user_email = st.selectbox('User', user_opts, key='remove_user')
        record = next((r for r in group_records if r.get('userEmail') == remove_user_email), None)
        if record and st.button('Delete?'):
            service.delete_user_group(record['id'])
            st.success('Deleted')
            st.rerun()


def render_group_management():
    st.header('Group Management')
    tabs = st.tabs(['Groups', 'UserGroups'])
    with tabs[0]:
        _groups_tab()
    with tabs[1]:
        _user_groups_tab()
