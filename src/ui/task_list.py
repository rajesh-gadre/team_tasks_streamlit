"""
Task list module for the Task Management System.
Handles rendering of task lists and related actions.
"""
import streamlit as st
from datetime import datetime
from typing import List, Callable

from src.database.models import Task, TaskStatus
from src.tasks.task_service import task_service

def render_task_list(tasks: List[Task], status: str, on_refresh: Callable = None):
    """
    Render a list of tasks with appropriate actions.
    
    Args:
        tasks: List of Task objects to render
        status: Status of tasks being displayed (active, completed, deleted)
        on_refresh: Callback function to refresh the task list
    """
    if not tasks:
        st.info(f"No {status.lower()} tasks found.")
        return
    
    # Get current user ID
    user_id = st.session_state.user.get('id')
    
    # Render each task as an expandable container
    for task in tasks:
        with st.expander(f"{task.title}", expanded=False):
            # Task details
            cols = st.columns([3, 1])
            
            with cols[0]:
                if task.description:
                    st.markdown(f"**Description:** {task.description}")
                
                if task.due_date:
                    due_date_str = task.due_date.strftime("%Y-%m-%d") if isinstance(task.due_date, datetime) else task.due_date
                    st.markdown(f"**Due Date:** {due_date_str}")
                
                if task.notes:
                    st.markdown(f"**Notes:** {task.notes}")
                
                # Show task history if available
                if task.updates and len(task.updates) > 0:
                    with st.expander("Task History"):
                        for update in sorted(task.updates, key=lambda x: x.get('timestamp', datetime.min), reverse=True):
                            timestamp = update.get('timestamp')
                            timestamp_str = timestamp.strftime("%Y-%m-%d %H:%M") if isinstance(timestamp, datetime) else str(timestamp)
                            st.text(f"{timestamp_str}: {update.get('updateText', 'Updated')}")
            
            # Task actions based on status
            with cols[1]:
                if status == TaskStatus.ACTIVE:
                    # Complete button
                    if st.button("Complete", key=f"complete_{task.id}"):
                        if task_service.complete_task(user_id, task.id):
                            st.success("Task marked as completed!")
                            if on_refresh:
                                on_refresh()
                        else:
                            st.error("Failed to complete task.")
                    
                    # Edit button
                    if st.button("Edit", key=f"edit_{task.id}"):
                        st.session_state.editing_task = task
                        st.rerun()
                    
                    # Delete button
                    if st.button("Delete", key=f"delete_{task.id}"):
                        if task_service.delete_task(user_id, task.id):
                            st.success("Task deleted!")
                            if on_refresh:
                                on_refresh()
                        else:
                            st.error("Failed to delete task.")
                
                elif status == TaskStatus.COMPLETED:
                    # Delete button
                    if st.button("Delete", key=f"delete_{task.id}"):
                        if task_service.delete_task(user_id, task.id):
                            st.success("Task deleted!")
                            if on_refresh:
                                on_refresh()
                        else:
                            st.error("Failed to delete task.")
                
                elif status == TaskStatus.DELETED:
                    # Restore button
                    if st.button("Restore", key=f"restore_{task.id}"):
                        if task_service.restore_task(user_id, task.id):
                            st.success("Task restored!")
                            if on_refresh:
                                on_refresh()
                        else:
                            st.error("Failed to restore task.")

def render_active_tasks():
    """Render active tasks list with refresh capability."""
    st.header("Active Tasks")
    
    # Add new task button
    if st.button("Add New Task", key="add_new_task"):
        st.session_state.adding_task = True
        st.rerun()
    
    # Get current user ID
    user_id = st.session_state.user.get('id')
    
    # Get active tasks
    tasks = task_service.get_active_tasks(user_id)
    
    # Define refresh function
    def refresh_tasks():
        st.session_state.refresh_active = True
        st.rerun()
    
    # Render task list
    render_task_list(tasks, TaskStatus.ACTIVE, refresh_tasks)

def render_completed_tasks():
    """Render completed tasks list with refresh capability."""
    st.header("Completed Tasks")
    
    # Get current user ID
    user_id = st.session_state.user.get('id')
    
    # Get completed tasks
    tasks = task_service.get_completed_tasks(user_id)
    
    # Define refresh function
    def refresh_tasks():
        st.session_state.refresh_completed = True
        st.rerun()
    
    # Render task list
    render_task_list(tasks, TaskStatus.COMPLETED, refresh_tasks)

def render_deleted_tasks():
    """Render deleted tasks list with refresh capability."""
    st.header("Deleted Tasks")
    
    # Get current user ID
    user_id = st.session_state.user.get('id')
    
    # Get deleted tasks
    tasks = task_service.get_deleted_tasks(user_id)
    
    # Define refresh function
    def refresh_tasks():
        st.session_state.refresh_deleted = True
        st.rerun()
    
    # Render task list
    render_task_list(tasks, TaskStatus.DELETED, refresh_tasks)
