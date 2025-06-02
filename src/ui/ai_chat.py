"""
AI chat module for the Task Management System.
Handles rendering of AI chat interface and interactions.
"""
import streamlit as st
import logging
from typing import Dict, Any

from src.ai.openai_service import openai_service

# Configure logging
logger = logging.getLogger(__name__)

def render_ai_chat():
    """Render AI chat interface."""
    st.header("AI Assistant")
    
    # Get current user ID (using email as the user identifier)
    user_id = st.session_state.user.get('email')
    
    # Initialize chat state if not exists
    if 'ai_input' not in st.session_state:
        st.session_state.ai_input = ""
    if 'ai_response' not in st.session_state:
        st.session_state.ai_response = None
    if 'ai_processing' not in st.session_state:
        st.session_state.ai_processing = False
    
    # Display information about the AI assistant
    st.markdown("""
    Talk with the AI assistant for help creating and/or updating your tasks. 
    """)
    
    # Input form
    with st.form(key="ai_chat_form"):
        # Text input
        ai_input = st.text_area("Your question", value=st.session_state.ai_input, height=100)
        
        # Submit button - always enabled, we'll check content later
        submit_button = st.form_submit_button("Submit")
    
    # Handle form submission
    if submit_button and ai_input.strip():
        # Store input in session state
        st.session_state.ai_input = ai_input
        
        # Set processing flag
        st.session_state.ai_processing = True
        
        try:
            # Process chat with OpenAI
            with st.spinner("Processing your question..."):
                # Append user_id to the input for the OpenAI service to extract
                ai_input_with_id = f"{ai_input}\n\nuser_id: {user_id}"
                result = openai_service.process_chat(user_id, ai_input_with_id)
                
                # Store response in session state
                st.session_state.ai_response = result.get('response')
                
                # Clear input after successful processing
                st.session_state.ai_input = ""
                
                # Reset processing flag
                st.session_state.ai_processing = False
                
                # Rerun to update UI
                st.rerun()
        except Exception as e:
            logger.error(f"Error processing AI chat: {str(e)}")
            st.error(f"Error processing your question: {str(e)}")
            st.session_state.ai_processing = False
    
    # Display AI response if available
    if st.session_state.ai_response:
        st.subheader("Response")
        st.markdown(st.session_state.ai_response)
        
        # Clear response button
        if st.button("Clear Response"):
            st.session_state.ai_response = None
            st.rerun()
    
    # Show processing indicator
    if st.session_state.ai_processing:
        st.spinner("Processing your question...")
