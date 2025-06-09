import streamlit as st
from src.ui.task_form import render_task_form
from src.ui.task_list import render_active_tasks, render_completed_tasks, render_deleted_tasks

def render_tasks_page():
    st.title('Tasks')
    tabs = st.tabs(['Active Tasks', 'Completed Tasks', 'Deleted Tasks'])
    with tabs[0]:
        if st.session_state.get('adding_task'):
            render_task_form()
        elif st.session_state.get('editing_task'):
            render_task_form(st.session_state.editing_task)
        else:
            render_active_tasks()
    with tabs[1]:
        render_completed_tasks()
    with tabs[2]:
        render_deleted_tasks()
