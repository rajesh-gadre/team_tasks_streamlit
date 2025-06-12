from datetime import datetime
from typing import Callable, List

import streamlit as st

from src.database.models import Task, TaskStatus
from src.tasks.task_service import get_task_service
from src.utils.time_utils import format_user_tz
from src.utils.sort_utils import sort_tasks
from src.utils.filter_utils import filter_tasks_by_tags

def render_task_list(tasks: List[Task], status: str, on_refresh: Callable=None):
    print(f"\n\n****{status=}\n\n")
    for task in tasks:
        print(f"task: {task.title=}, {task.id=}, {task.status=}")
    print("***************************")

    if not tasks:
        st.info(f'No {status.lower()} tasks found.')
        return
    user_id = st.session_state.user.get('email')
    if status == TaskStatus.ACTIVE:
        sort_opts = ['Title', 'Due Date']
    elif status == TaskStatus.COMPLETED:
        sort_opts = ['Title', 'Completed Date']
    else:
        sort_opts = ['Title', 'Deleted Date']
    sort_by = st.selectbox('Sort by', sort_opts, key=f'sort_{status}')
    descending = st.checkbox('Descending', key=f'desc_{status}', value=False)
    tasks = sort_tasks(tasks, sort_by, descending)
    if status == TaskStatus.ACTIVE:
        cols = ['Title', 'Due Date', 'Actions', 'Details']
    elif status == TaskStatus.COMPLETED:
        cols = ['Title', 'Completed Date', 'Actions', 'Details']
    elif status == TaskStatus.DELETED:
        cols = ['Title', 'Deleted Date', 'Actions', 'Details']
    table = st.container()
    if status == TaskStatus.ACTIVE:
        st.markdown('\n            <style>\n            div[data-testid="column"]:not(:last-child) {\n                border-right: 1px solid #DDD;\n            }\n            hr.task-separator {\n                margin-top: 4px;\n                margin-bottom: 4px;\n            }\n            </style>\n            ', unsafe_allow_html=True)
    with table:
        if status == TaskStatus.ACTIVE:
            header = st.columns([3, 1, 2, 1])
            header[0].write('**Title**')
            header[1].write('**Due Date**')
            header[2].write('**Actions**')
            header[3].write('**Details**')
        else:
            header = st.columns([3, 2, 2, 1])
            header[0].write('**Title**')
            header[1].write('**Date**')
            header[2].write('**Actions**')
            header[3].write('**Details**')
        st.markdown("<hr class='task-separator'>", unsafe_allow_html=True)
        for idx, task in enumerate(tasks):
            print(f"In FOR LOOP. task: {task.title=}, {task.id=}, {task.status=}")
            if status == TaskStatus.ACTIVE:
                row = st.columns([3, 1, 2, 1])
                row[0].write(task.title)
                row[1].write(format_user_tz(task.due_date, '%Y-%m-%d') if task.due_date else 'N/A')
                action_col = row[2]
                details_col = row[3]
            else:
                row = st.columns([3, 2, 2, 1])
                row[0].write(task.title)
                row[1].write(format_user_tz(task.due_date, '%Y-%m-%d') if task.due_date else 'N/A')
                action_col = row[2]
                details_col = row[3]
            if status == TaskStatus.ACTIVE:
                action_buttons = action_col.columns(3)
                if action_buttons[0].button('✓', key=f'to_complete_{task.id}_{idx}', help='Mark as completed'):
                    if get_task_service().complete_task(user_id, task.id):
                        st.success('Task marked as completed!')
                        if on_refresh:
                            on_refresh()
                    else:
                        st.error('Failed to complete task.')
                if action_buttons[1].button('✎', key=f'to_edit_{task.id}_{idx}', help='Edit task'):
                    st.session_state.editing_task = task
                    st.rerun()
                if action_buttons[2].button('🗑', key=f'to_delete_{task.id}_{idx}', help='Delete task'):
                    if get_task_service().delete_task(user_id, task.id):
                        st.success('Task deleted!')
                        if on_refresh:
                            on_refresh()
                    else:
                        st.error('Failed to delete task.')
            elif status == TaskStatus.COMPLETED:
                if action_col.button('🗑', key=f'to_delete_{task.id}_{idx}', help='Delete task'):
                    if get_task_service().delete_task(user_id, task.id):
                        st.success('Task deleted!')
                        if on_refresh:
                            on_refresh()
                    else:
                        st.error('Failed to delete task.')
            elif status == TaskStatus.DELETED:
                if action_col.button('↩', key=f'to_restore_{task.id}_{idx}', help='Restore task'):
                    if get_task_service().restore_task(user_id, task.id):
                        st.success('Task restored!')
                        if on_refresh:
                            on_refresh()
                    else:
                        st.error('Failed to restore task.')
            if details_col.button('👁', key=f'details_{task.id}_{idx}', help='View details'):
                if 'task_details' not in st.session_state:
                    st.session_state.task_details = {}
                if task.id in st.session_state.task_details:
                    del st.session_state.task_details[task.id]
                else:
                    detail = get_task_service().get_task(task.user_id, task.id)
                    st.session_state.task_details[task.id] = detail
                st.rerun()
            if 'task_details' in st.session_state and task.id in st.session_state.task_details:
                with st.expander('Task Details', expanded=True):
                    detail = st.session_state.task_details.get(task.id)
                    st.json({k: str(v) for k, v in vars(detail).items()})
            st.markdown("<hr class='task-separator'>", unsafe_allow_html=True)

def render_active_tasks():
    st.header('Active Tasks')
    user_id = st.session_state.user.get('email')
    tasks = get_task_service().get_active_tasks(user_id)
    tag_query = st.text_input('Search Tags', key='tags_active')
    tasks = filter_tasks_by_tags(tasks, tag_query)
    st.write(f'Total tasks: {len(tasks)}')

    def refresh_tasks():
        st.session_state.refresh_active = True
        st.rerun()
    render_task_list(tasks, TaskStatus.ACTIVE, refresh_tasks)

def render_completed_tasks():
    st.header('Completed Tasks')
    user_id = st.session_state.user.get('email')
    tasks = get_task_service().get_completed_tasks(user_id)
    tag_query = st.text_input('Search Tags', key='tags_completed')
    tasks = filter_tasks_by_tags(tasks, tag_query)
    st.write(f'Total tasks: {len(tasks)}')

    def refresh_tasks():
        st.session_state.refresh_completed = True
        st.rerun()
    render_task_list(tasks, TaskStatus.COMPLETED, refresh_tasks)

def render_deleted_tasks():
    st.header('Deleted Tasks')
    user_id = st.session_state.user.get('email')
    tasks = get_task_service().get_deleted_tasks(user_id)
    tag_query = st.text_input('Search Tags', key='tags_deleted')
    tasks = filter_tasks_by_tags(tasks, tag_query)
    st.write(f'Total tasks: {len(tasks)}')

    def refresh_tasks():
        st.session_state.refresh_deleted = True
        st.rerun()
    render_task_list(tasks, TaskStatus.DELETED, refresh_tasks)
