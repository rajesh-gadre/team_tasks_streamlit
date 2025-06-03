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
    user_id = st.session_state.user.get('email')
    if status == TaskStatus.ACTIVE:
        cols = ["Title", "Description", "Notes", "Due Date", "History", "Actions"]
    elif status == TaskStatus.COMPLETED:
        cols = ["Title", "Completed Date", "Actions", "Details"]
    elif status == TaskStatus.DELETED:
        cols = ["Title", "Deleted Date", "Actions", "Details"]
    table = st.container()
    with table:
        if status == TaskStatus.ACTIVE:
            header = st.columns([2, 2, 2, 1, 2, 1])
            header[0].write("**Title**")
            header[1].write("**Description**")
            header[2].write("**Notes**")
            header[3].write("**Due Date**")
            header[4].write("**History**")
            header[5].write("**Actions**")
        else:
            header = st.columns([3, 2, 2, 1])
            header[0].write("**Title**")
            header[1].write("**Date**")
            header[2].write("**Actions**")
            header[3].write("**Details**")
        st.markdown("---")
        
        for task in tasks:
            if status == TaskStatus.ACTIVE:
                row = st.columns([2, 2, 2, 1, 2, 1])
                row[0].write(task.title)
                
                # Description column
                description_text = task.description if task.description else "N/A"
                if len(description_text) > 50:
                    description_text = description_text[:47] + "..."
                row[1].write(description_text)
                
                # Notes column
                notes_text = task.notes if task.notes else "N/A"
                if len(notes_text) > 50:
                    notes_text = notes_text[:47] + "..."
                row[2].write(notes_text)
                
                # Due date column
                if task.due_date:
                    due_date_str = task.due_date.strftime("%Y-%m-%d") if isinstance(task.due_date, datetime) else task.due_date
                    row[3].write(due_date_str)
                else:
                    row[3].write("N/A")
                
                # History column
                if task.updates and len(task.updates) > 0:
                    # Get the most recent update
                    sorted_updates = sorted(task.updates, key=lambda x: x.get('timestamp', datetime.min), reverse=True)
                    latest_update = sorted_updates[0]
                    timestamp = latest_update.get('timestamp')
                    timestamp_str = timestamp.strftime("%Y-%m-%d") if isinstance(timestamp, datetime) else str(timestamp)
                    update_text = latest_update.get('updateText', 'Updated')
                    
                    # Truncate if too long
                    if len(update_text) > 30:
                        update_text = update_text[:27] + "..."
                    
                    history_text = f"{timestamp_str}: {update_text}"
                    
                    # Add a tooltip to show all updates on hover
                    all_updates = "\n".join([f"{u.get('timestamp').strftime('%Y-%m-%d %H:%M') if isinstance(u.get('timestamp'), datetime) else u.get('timestamp')}: {u.get('updateText', 'Updated')}" for u in sorted_updates[:5]])
                    if len(sorted_updates) > 5:
                        all_updates += "\n...and more"
                    
                    row[4].write(history_text, help=all_updates)
                else:
                    row[4].write("-")
                    
                action_col = row[5]
            else:
                row = st.columns([3, 2, 2, 1])
                row[0].write(task.title)
                if task.due_date:
                    due_date_str = task.due_date.strftime("%Y-%m-%d") if isinstance(task.due_date, datetime) else task.due_date
                    row[1].write(due_date_str)
                else:
                    row[1].write("N/A")
                action_col = row[2]
            if status == TaskStatus.ACTIVE:
                action_buttons = action_col.columns(3)
                if action_buttons[0].button("✓", key=f"complete_{task.id}", help="Mark as completed"):
                    if task_service.complete_task(user_id, task.id):
                        st.success("Task marked as completed!")
                        if on_refresh:
                            on_refresh()
                    else:
                        st.error("Failed to complete task.")
                if action_buttons[1].button("✎", key=f"edit_{task.id}", help="Edit task"):
                    st.session_state.editing_task = task
                    st.rerun()
                if action_buttons[2].button("🗑", key=f"delete_{task.id}", help="Delete task"):
                    if task_service.delete_task(user_id, task.id):
                        st.success("Task deleted!")
                        if on_refresh:
                            on_refresh()
                    else:
                        st.error("Failed to delete task.")
            
            elif status == TaskStatus.COMPLETED:
                if action_col.button("🗑", key=f"delete_{task.id}", help="Delete task"):
                    if task_service.delete_task(user_id, task.id):
                        st.success("Task deleted!")
                        if on_refresh:
                            on_refresh()
                    else:
                        st.error("Failed to delete task.")
            elif status == TaskStatus.DELETED:
                if action_col.button("↩", key=f"restore_{task.id}", help="Restore task"):
                    if task_service.restore_task(user_id, task.id):
                        st.success("Task restored!")
                        if on_refresh:
                            on_refresh()
                    else:
                        st.error("Failed to restore task.")
            
            # Only show details button for completed and deleted tasks
            if status != TaskStatus.ACTIVE:
                if row[3].button("👁", key=f"details_{task.id}", help="View details"):
                    if 'task_details' not in st.session_state:
                        st.session_state.task_details = {}
                    if task.id in st.session_state.task_details:
                        del st.session_state.task_details[task.id]
                    else:
                        st.session_state.task_details[task.id] = True
                    st.rerun()
                if 'task_details' in st.session_state and task.id in st.session_state.task_details:
                    with st.expander("Task Details", expanded=True):
                        if task.description:
                            st.markdown(f"**Description:** {task.description}")
                        if task.notes:
                            st.markdown(f"**Notes:** {task.notes}")
                        if task.updates and len(task.updates) > 0:
                            st.subheader("Task History")
                            for update in sorted(task.updates, key=lambda x: x.get('timestamp', datetime.min), reverse=True):
                                timestamp = update.get('timestamp')
                                timestamp_str = timestamp.strftime("%Y-%m-%d %H:%M") if isinstance(timestamp, datetime) else str(timestamp)
                                st.text(f"{timestamp_str}: {update.get('updateText', 'Updated')}")
            
            # For active tasks, provide a button to show full history
            if status == TaskStatus.ACTIVE and task.updates and len(task.updates) > 1:  # Only if there's more than one update
                if row[4].button("📜", key=f"history_{task.id}", help="View full history"):
                    if 'task_history' not in st.session_state:
                        st.session_state.task_history = {}
                    if task.id in st.session_state.task_history:
                        del st.session_state.task_history[task.id]
                    else:
                        st.session_state.task_history[task.id] = True
                    st.rerun()
                
                # Show full history in an expander if requested
                if 'task_history' in st.session_state and task.id in st.session_state.task_history:
                    with st.expander("Full Task History", expanded=True):
                        for update in sorted(task.updates, key=lambda x: x.get('timestamp', datetime.min), reverse=True):
                            timestamp = update.get('timestamp')
                            timestamp_str = timestamp.strftime("%Y-%m-%d %H:%M") if isinstance(timestamp, datetime) else str(timestamp)
                            st.text(f"{timestamp_str}: {update.get('updateText', 'Updated')}")
            st.markdown("---")

def render_active_tasks():
    """Render active tasks list with refresh capability."""
    st.header("Active Tasks")
    if st.button("Add New Task", key="add_new_task"):
        st.session_state.adding_task = True
        st.rerun()
    user_id = st.session_state.user.get('email')
    tasks = task_service.get_active_tasks(user_id)
    def refresh_tasks():
        st.session_state.refresh_active = True
        st.rerun()
    render_task_list(tasks, TaskStatus.ACTIVE, refresh_tasks)

def render_completed_tasks():
    """Render completed tasks list with refresh capability."""
    st.header("Completed Tasks")
    user_id = st.session_state.user.get('email')
    tasks = task_service.get_completed_tasks(user_id)
    def refresh_tasks():
        st.session_state.refresh_completed = True
        st.rerun()
    render_task_list(tasks, TaskStatus.COMPLETED, refresh_tasks)

def render_deleted_tasks():
    """Render deleted tasks list with refresh capability."""
    st.header("Deleted Tasks")
    user_id = st.session_state.user.get('email')
    tasks = task_service.get_deleted_tasks(user_id)
    def refresh_tasks():
        st.session_state.refresh_deleted = True
        st.rerun()
    render_task_list(tasks, TaskStatus.DELETED, refresh_tasks)
