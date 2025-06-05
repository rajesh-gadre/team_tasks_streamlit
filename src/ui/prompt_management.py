"""UI components for managing AI prompts."""
import streamlit as st
from src.ai.prompt_service import get_prompt_service
from src.database.models import PromptStatus


def render_prompt_management():
    """Render prompt management interface."""
    st.header("Prompt Management")

    try:
        prompts = get_prompt_service().get_all_prompts()
    except Exception as e:
        st.error(f"Error loading prompts: {e}")
        return

    if not prompts:
        st.info("No prompts found.")
        return

    for prompt in prompts:
        with st.form(key=f"prompt_form_{prompt.id}"):
            text = st.text_area("Prompt Text", value=prompt.text, key=f"text_{prompt.id}")
            submit = st.form_submit_button("Update")

        if submit:
            if not text.strip():
                st.error("Prompt text cannot be empty")
            else:
                data = {"text": text}
                try:
                    if get_prompt_service().update_prompt(prompt.id, data):
                        st.success("Prompt updated successfully!")
                        st.rerun()
                    else:
                        st.error("Failed to update prompt")
                except Exception as e:
                    st.error(f"Failed to update prompt: {e}")
