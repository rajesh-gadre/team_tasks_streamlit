import streamlit as st
from src.groups.user_group_service import get_user_group_service
from src.tasks.task_service import get_task_service


def render_group_tasks():
    st.header('Group Tasks')
    ug_service = get_user_group_service()
    groups = ug_service.get_groups_for_user(st.session_state.get('userId'))
    names = [''] + [g.get('groupName', '') for g in groups]
    selected = st.selectbox('Group', names)
    if selected:
        members = [r.get('userEmail') for r in ug_service.get_user_groups() if r.get('groupName') == selected]
        tasks = [t for t in get_task_service().get_all_tasks() if t.user_id in members]
        tasks.sort(key=lambda t: t.updated_at or t.created_at, reverse=True)
        for task in tasks:
            st.write(f"{task.title} - {task.user_id} - {task.status}")
