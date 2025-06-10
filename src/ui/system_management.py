import streamlit as st
from src.ui.prompt_management import render_prompt_management
from src.ui.group_management import render_group_management
from src.ui.task_assignment import render_task_assignment
from src.ui.run_tests import render_run_tests

def render_system_management():
    st.title('System Management')
    tabs = st.tabs(['Prompt Management', 'Group Management', 'Assign Tasks', 'Coverage'])
    with tabs[0]:
        render_prompt_management()
    with tabs[1]:
        render_group_management()
    with tabs[2]:
        render_task_assignment()
    with tabs[3]:
        render_run_tests()
