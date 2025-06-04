"""
AI chat module for the Task Management System.
Handles rendering of AI chat interface and interactions.
"""
import streamlit as st
import logging
from typing import Dict, Any
from src.ai.openai_service import openai_service
import traceback

logger = logging.getLogger(__name__)

def render_ai_chat():
    """Render AI chat interface."""
    st.header("AI Assistant")
    user_id = st.session_state.user.get('email')
    if 'ai_input' not in st.session_state:
        st.session_state.ai_input = ""
    if 'ai_response' not in st.session_state:
        st.session_state.ai_response = None
    if 'ai_processing' not in st.session_state:
        st.session_state.ai_processing = False
    st.markdown("""
    Talk with the AI assistant for help creating and/or updating your tasks. 
    """)
    if st.session_state.ai_processing:
        try:
            ai_input_with_id = st.session_state.get(
                "ai_input_with_id", f"{st.session_state.ai_input}\n\nuser_id: {user_id}"
            )
            result = openai_service.process_chat(user_id, ai_input_with_id)
            if result:
                st.session_state.ai_response = result.get("response")
                st.session_state.ai_input = ""
                st.session_state.ai_processing = False
                st.session_state.ai_input_with_id = ""
                st.rerun()
        except Exception as e:
            logger.error(f"Error processing AI chat: {str(e)}")
            st.error(f"Error processing your question: {str(e)}")
            st.session_state.ai_processing = False
            traceback.print_exc()

    with st.form(key="ai_chat_form"):
        ai_input = st.text_area(
            "Your question", value=st.session_state.ai_input, height=100
        )
        submit_button = st.form_submit_button("Submit")

    if submit_button and ai_input.strip():
        st.session_state.ai_input = ai_input
        st.session_state.ai_input_with_id = f"{ai_input}\n\nuser_id: {user_id}"
        st.session_state.ai_processing = True
        st.rerun()
    if st.session_state.ai_response:
        st.subheader("Response")
        st.markdown(st.session_state.ai_response)
        if st.button("Clear Response"):
            st.session_state.ai_response = None
            st.rerun()
