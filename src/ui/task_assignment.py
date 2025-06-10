import streamlit as st
from src.tasks.task_service import get_task_service
from src.users.user_service import get_user_service


def render_task_assignment():
    st.header('Assign Tasks')
    ts = get_task_service()
    tasks = ts.get_all_tasks()
    users = get_user_service().get_users()
    task_opts = {f"{t.title} ({t.user_id})": t.id for t in tasks}
    selected_labels = st.multiselect('Tasks', list(task_opts.keys()))
    user_opts = {u.get('userName') or u['userEmail']: u['userId'] for u in users}
    selected_user = st.selectbox('Assign To', [''] + list(user_opts.keys()))
    if st.button('Assign') and selected_labels and selected_user:
        ids = [task_opts[l] for l in selected_labels]
        if ts.assign_tasks(ids, user_opts[selected_user]):
            st.success('Tasks assigned')
        else:
            st.error('Assignment failed')
