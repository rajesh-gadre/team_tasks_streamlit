import streamlit as st
from src.ui.task_list import render_completed_tasks

def main():
    st.title('Completed Tasks')
    render_completed_tasks()
if __name__ == '__main__':
    main()
