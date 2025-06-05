"""
Task form module for the Task Management System.
Handles rendering of task creation and editing forms.
"""
import streamlit as st
from datetime import datetime
from typing import Dict, Optional, Any
from src.database.models import Task
from src.tasks.task_service import get_task_service 

def render_task_form(task: Optional[Task] = None):
    task_service = get_task_service()
    """
    Render a form for creating or editing a task.
    
    Args:
        task: Task object to edit, or None for a new task
    """
    # Set form title based on whether we're editing or creating
    if task:
        st.header("Edit Task")
    else:
        st.header("Create New Task")
    
    # Create form
    with st.form(key="task_form"):
        # Task title (required)
        title = st.text_input("Title", value=task.title if task else "")
        if not title:
            st.warning("Title is required")
        
        # Task description (optional)
        description = st.text_area("Description", value=task.description if task else "")
        
        # Due date (optional)
        due_date_value = None
        if task and task.due_date:
            if isinstance(task.due_date, datetime):
                due_date_value = task.due_date.date()
            elif isinstance(task.due_date, str):
                try:
                    due_date_value = datetime.strptime(task.due_date, "%Y-%m-%d").date()
                except ValueError:
                    due_date_value = None
        
        due_date = st.date_input("Due Date", value=due_date_value if due_date_value else None)
        
        # Notes (optional)
        notes = st.text_area("Notes", value=task.notes if task else "")
        
        # Form submission buttons
        cols = st.columns([1, 1])
        with cols[0]:
            submit_button = st.form_submit_button("Save Task")
        with cols[1]:
            cancel_button = st.form_submit_button("Cancel")
    
    # Handle form submission
    if submit_button:
        # Validate form
        if not title:
            st.error("Title is required")
            return
        
        # Get current user ID (using email as the user identifier)
        user_id = st.session_state.user.get('email')
        
        # Prepare task data
        # Convert date to datetime for Firestore compatibility
        due_date_value = None
        if due_date and due_date != datetime.today().date():
            # Convert date to datetime at midnight for consistent storage
            due_date_value = datetime.combine(due_date, datetime.min.time())
            
        task_data = {
            'title': title,
            'description': description if description else None,
            'due_date': due_date_value,
            'notes': notes if notes else None
        }
        
        # Create or update task
        if task:
            # Update existing task
            if task_service.update_task(user_id, task.id, task_data):
                st.success("Task updated successfully!")
                # Clear editing state
                if 'editing_task' in st.session_state:
                    del st.session_state.editing_task
                st.rerun()
            else:
                st.error("Failed to update task")
        else:
            # Create new task
            task_id = task_service.create_task(user_id, task_data)
            if task_id:
                st.success("Task created successfully!")
                # Clear adding state
                if 'adding_task' in st.session_state:
                    del st.session_state.adding_task
                st.rerun()
            else:
                st.error("Failed to create task")
    
    # Handle cancel button
    if cancel_button:
        # Clear form state
        if 'editing_task' in st.session_state:
            del st.session_state.editing_task
        if 'adding_task' in st.session_state:
            del st.session_state.adding_task
        st.rerun()
