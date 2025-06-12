import streamlit as st
from datetime import datetime
from typing import Dict, Optional, Any
from src.database.models import Task
from src.tasks.task_service import get_task_service
from src.users.user_service import get_user_service

def render_task_form(task: Optional[Task]=None):
    task_service = get_task_service()
    '\n    Render a form for creating or editing a task.\n    \n    Args:\n        task: Task object to edit, or None for a new task\n    '
    if task:
        st.header('Edit Task')
    else:
        st.header('Create New Task')
    with st.form(key='task_form'):
        title = st.text_input('Title', value=task.title if task else '')
        if not title:
            st.warning('Title is required')
        description = st.text_area('Description', value=task.description if task else '')
        due_date_value = None
        if task and task.due_date:
            if isinstance(task.due_date, datetime):
                due_date_value = task.due_date.date()
            elif isinstance(task.due_date, str):
                try:
                    due_date_value = datetime.strptime(task.due_date, '%Y-%m-%d').date()
                except ValueError:
                    due_date_value = None
        due_date = st.date_input('Due Date', value=due_date_value if due_date_value else None)
        tags_str = ', '.join(task.tags) if task and task.tags else ''
        tags_input = st.text_input('Tags (comma separated)', value=tags_str)
        notes = st.text_area('Notes', value=task.notes if task else '')
        users = get_user_service().get_users()
        opts = {u.get('userName') or u['userEmail']: u['userEmail'] for u in users}
        default_label = next((k for k, v in opts.items() if v == st.session_state.user.get('email')), '')
        assign_label = st.selectbox('Assign To', list(opts.keys()), index=list(opts.keys()).index(default_label) if default_label in opts else 0)
        cols = st.columns([1, 1])
        with cols[0]:
            submit_button = st.form_submit_button('Save Task')
        with cols[1]:
            cancel_button = st.form_submit_button('Cancel')
    if submit_button:
        if not title:
            st.error('Title is required')
            return
        user_id = opts.get(assign_label, st.session_state.user.get('email'))
        due_date_value = None
        if due_date and due_date != datetime.today().date():
            due_date_value = datetime.combine(due_date, datetime.min.time())
        user = st.session_state.user
        tags = [t.strip() for t in tags_input.split(',') if t.strip()]
        task_data = {'title': title, 'description': description if description else None, 'due_date': due_date_value, 'notes': notes if notes else None, 'owner_id': user.get('userId', user.get('email')), 'owner_email': user.get('email'), 'owner_name': user.get('name'), 'tags': tags}
        if task:
            if task_service.update_task(user_id, task.id, task_data):
                st.success('Task updated successfully!')
                if 'editing_task' in st.session_state:
                    del st.session_state.editing_task
                st.rerun()
            else:
                st.error('Failed to update task')
        else:
            task_id = task_service.create_task(user_id, task_data)
            if task_id:
                st.success('Task created successfully!')
                st.rerun()
            else:
                st.error('Failed to create task')
    if cancel_button:
        if 'editing_task' in st.session_state:
            del st.session_state.editing_task
        st.rerun()
