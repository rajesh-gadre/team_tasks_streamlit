import streamlit as st
from typing import List, Tuple
from src.database.models import Task, TaskStatus
from src.groups.user_group_service import get_user_group_service
from src.tasks.task_service import get_task_service
from src.utils.time_utils import format_user_tz
from src.utils.sort_utils import sort_group_tasks


def _get_group_tasks(status: str) -> List[Tuple[str, Task]]:
    ug_service = get_user_group_service()
    groups = ug_service.get_groups_for_user(st.session_state.get('userId'))
    records = ug_service.get_user_groups()
    all_tasks = get_task_service().get_all_tasks()
    results: List[Tuple[str, Task]] = []
    for g in groups:
        name = g.get('groupName', '')
        members = [r.get('userEmail') for r in records if r.get('groupName') == name]
        for t in all_tasks:
            if t.user_id in members and t.status == status:
                results.append((name, t))
    results.sort(key=lambda x: x[1].updated_at or x[1].created_at, reverse=True)
    return results


def _render_group_task_list(tasks: List[Tuple[str, Task]], status: str):
    if not tasks:
        st.info(f'No {status.lower()} tasks found.')
        return
    user_id = st.session_state.user.get('email')
    if status == TaskStatus.ACTIVE:
        sort_opts = ['Group', 'Title', 'Due Date']
    elif status == TaskStatus.COMPLETED:
        sort_opts = ['Group', 'Title', 'Completed Date']
    else:
        sort_opts = ['Group', 'Title', 'Deleted Date']
    sort_by = st.selectbox('Sort by', sort_opts, key=f'gsort_{status}')
    descending = st.checkbox('Descending', key=f'gdesc_{status}', value=False)
    tasks = sort_group_tasks(tasks, sort_by, descending)
    if status == TaskStatus.ACTIVE:
        header = st.columns([2, 3, 1, 2, 1])
        header[0].write('**Group**')
        header[1].write('**Title**')
        header[2].write('**Due Date**')
        header[3].write('**Actions**')
        header[4].write('**Details**')
    else:
        header = st.columns([2, 3, 2, 2, 1])
        header[0].write('**Group**')
        header[1].write('**Title**')
        header[2].write('**Date**')
        header[3].write('**Actions**')
        header[4].write('**Details**')
    st.markdown("<hr class='task-separator'>", unsafe_allow_html=True)
    for idx, (group_name, task) in enumerate(tasks):
        if status == TaskStatus.ACTIVE:
            row = st.columns([2, 3, 1, 2, 1])
            row[0].write(group_name)
            row[1].write(task.title)
            row[2].write(format_user_tz(task.due_date, '%Y-%m-%d') if task.due_date else 'N/A')
            action_col = row[3]
            details_col = row[4]
        else:
            row = st.columns([2, 3, 2, 2, 1])
            row[0].write(group_name)
            row[1].write(task.title)
            row[2].write(format_user_tz(task.due_date, '%Y-%m-%d') if task.due_date else 'N/A')
            action_col = row[3]
            details_col = row[4]
        if status == TaskStatus.ACTIVE:
            action_buttons = action_col.columns(3)
            if action_buttons[0].button('✓', key=f'to_complete_{task.id}_{idx}'):
                if get_task_service().complete_task(user_id, task.id):
                    st.success('Task marked as completed!')
                    st.rerun()
                else:
                    st.error('Failed to complete task.')
            if action_buttons[1].button('✎', key=f'to_edit_{task.id}_{idx}'):
                st.session_state.editing_task = task
                st.rerun()
            if action_buttons[2].button('🗑', key=f'to_delete_{task.id}_{idx}'):
                if get_task_service().delete_task(user_id, task.id):
                    st.success('Task deleted!')
                    st.rerun()
                else:
                    st.error('Failed to delete task.')
        elif status == TaskStatus.COMPLETED:
            if action_col.button('🗑', key=f'to_delete_{task.id}_{idx}'):
                if get_task_service().delete_task(user_id, task.id):
                    st.success('Task deleted!')
                    st.rerun()
                else:
                    st.error('Failed to delete task.')
        elif status == TaskStatus.DELETED:
            if action_col.button('↩', key=f'to_restore_{task.id}_{idx}'):
                if get_task_service().restore_task(user_id, task.id):
                    st.success('Task restored!')
                    st.rerun()
                else:
                    st.error('Failed to restore task.')
        if details_col.button('👁', key=f'details_{task.id}_{idx}'):
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


def render_group_tasks(status: str):
    tasks = _get_group_tasks(status)
    st.write(f'Total tasks: {len(tasks)}')
    _render_group_task_list(tasks, status)


def render_group_active_tasks():
    st.header('Active Tasks')
    render_group_tasks(TaskStatus.ACTIVE)


def render_group_completed_tasks():
    st.header('Completed Tasks')
    render_group_tasks(TaskStatus.COMPLETED)


def render_group_deleted_tasks():
    st.header('Deleted Tasks')
    render_group_tasks(TaskStatus.DELETED)
