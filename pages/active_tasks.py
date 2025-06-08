import streamlit as st
from src.ui.task_form import render_task_form
from src.ui.task_list import render_active_tasks

def main():
    st.title('Active Tasks')
    if st.session_state.get('adding_task'):
        render_task_form()
    elif st.session_state.get('editing_task'):
        render_task_form(st.session_state.editing_task)
    else:
        render_active_tasks()
if __name__ == '__main__':
    main()
