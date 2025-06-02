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
    
    # Get current user ID (using email as the user identifier)
    user_id = st.session_state.user.get('email')
    
    # Create a table for tasks
    # Define columns based on status
    if status == TaskStatus.ACTIVE:
        cols = ["Title", "Due Date", "Actions", "Details"]
    elif status == TaskStatus.COMPLETED:
        cols = ["Title", "Completed Date", "Actions", "Details"]
    elif status == TaskStatus.DELETED:
        cols = ["Title", "Deleted Date", "Actions", "Details"]
    
    # Create the table
    table = st.container()
    with table:
        # Create header row
        header = st.columns([3, 2, 2, 1])
        header[0].write("**Title**")
        header[1].write("**Due Date**")
        header[2].write("**Actions**")
        header[3].write("**Details**")
        
        # Add a separator
        st.markdown("---")
        
        # Create a row for each task
        for task in tasks:
            row = st.columns([3, 2, 2, 1])
            
            # Title column
            row[0].write(task.title)
            
            # Date column
            if task.due_date:
                due_date_str = task.due_date.strftime("%Y-%m-%d") if isinstance(task.due_date, datetime) else task.due_date
                row[1].write(due_date_str)
            else:
                row[1].write("N/A")
            
            # Actions column
            action_col = row[2]
            if status == TaskStatus.ACTIVE:
                # Use horizontal layout for buttons
                action_buttons = action_col.columns(3)
                
                # Complete button
                if action_buttons[0].button("✓", key=f"complete_{task.id}", help="Mark as completed"):
                    if task_service.complete_task(user_id, task.id):
                        st.success("Task marked as completed!")
                        if on_refresh:
                            on_refresh()
                    else:
                        st.error("Failed to complete task.")
                
                # Edit button
                if action_buttons[1].button("✎", key=f"edit_{task.id}", help="Edit task"):
                    st.session_state.editing_task = task
                    st.rerun()
                
                # Delete button
                if action_buttons[2].button("🗑", key=f"delete_{task.id}", help="Delete task"):
                    if task_service.delete_task(user_id, task.id):
                        st.success("Task deleted!")
                        if on_refresh:
                            on_refresh()
                    else:
                        st.error("Failed to delete task.")
            
            elif status == TaskStatus.COMPLETED:
                # Delete button
                if action_col.button("🗑", key=f"delete_{task.id}", help="Delete task"):
                    if task_service.delete_task(user_id, task.id):
                        st.success("Task deleted!")
                        if on_refresh:
                            on_refresh()
                    else:
                        st.error("Failed to delete task.")
            
            elif status == TaskStatus.DELETED:
                # Restore button
                if action_col.button("↩", key=f"restore_{task.id}", help="Restore task"):
                    if task_service.restore_task(user_id, task.id):
                        st.success("Task restored!")
                        if on_refresh:
                            on_refresh()
                    else:
                        st.error("Failed to restore task.")
            
            # Details column - button to show task details
            if row[3].button("👁", key=f"details_{task.id}", help="View details"):
                # Store the task ID in session state for details view
                if 'task_details' not in st.session_state:
                    st.session_state.task_details = {}
                
                # Toggle details view
                if task.id in st.session_state.task_details:
                    del st.session_state.task_details[task.id]
                else:
                    st.session_state.task_details[task.id] = True
                st.rerun()
            
            # Show task details if expanded
            if 'task_details' in st.session_state and task.id in st.session_state.task_details:
                with st.expander("Task Details", expanded=True):
                    if task.description:
                        st.markdown(f"**Description:** {task.description}")
                    
                    if task.notes:
                        st.markdown(f"**Notes:** {task.notes}")
                    
                    # Show task history if available
                    if task.updates and len(task.updates) > 0:
                        st.subheader("Task History")
                        for update in sorted(task.updates, key=lambda x: x.get('timestamp', datetime.min), reverse=True):
                            timestamp = update.get('timestamp')
                            timestamp_str = timestamp.strftime("%Y-%m-%d %H:%M") if isinstance(timestamp, datetime) else str(timestamp)
                            st.text(f"{timestamp_str}: {update.get('updateText', 'Updated')}")
            
            # Add a separator between tasks
            st.markdown("---")

def render_active_tasks():
    """Render active tasks list with refresh capability."""
    st.header("Active Tasks")
    
    # Add new task button
    if st.button("Add New Task", key="add_new_task"):
        st.session_state.adding_task = True
        st.rerun()
    
    # Get current user ID (using email as the user identifier)
    user_id = st.session_state.user.get('email')
    
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
    
    # Get current user ID (using email as the user identifier)
    user_id = st.session_state.user.get('email')
    
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
    
    # Get current user ID (using email as the user identifier)
    user_id = st.session_state.user.get('email')
    
    # Get deleted tasks
    tasks = task_service.get_deleted_tasks(user_id)
    
    # Define refresh function
    def refresh_tasks():
        st.session_state.refresh_deleted = True
        st.rerun()
    
    # Render task list
    render_task_list(tasks, TaskStatus.DELETED, refresh_tasks)
