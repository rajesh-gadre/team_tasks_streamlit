"""
Deleted Tasks page for the Task Management System.
"""
import streamlit as st
from src.ui.task_list import render_deleted_tasks

def main():
    st.title("Deleted Tasks")
    render_deleted_tasks()

if __name__ == "__main__":
    main()
