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

    names = sorted({p.prompt_name for p in prompts})
    prompt_name = st.selectbox("Select Prompt", names)

    selected = [p for p in prompts if p.prompt_name == prompt_name]
    selected.sort(key=lambda p: p.version, reverse=True)

    for prompt in selected:
        with st.form(key=f"prompt_form_{prompt.id}"):
            st.write(f"Version {prompt.version} (Status: {prompt.status})")
            text = st.text_area("Prompt Text", value=prompt.text, key=f"text_{prompt.id}")
            col1, col2 = st.columns(2)
            submit = col1.form_submit_button("Update")
            activate = col2.form_submit_button("Set Active")

        if submit:
            if not text.strip():
                st.error("Prompt text cannot be empty")
            else:
                data = {"text": text}
                try:
                    if get_prompt_service().update_prompt(prompt.id, data):
                        st.success("New version created successfully!")
                        st.rerun()
                    else:
                        st.error("Failed to update prompt")
                except Exception as e:
                    st.error(f"Failed to update prompt: {e}")

        if activate:
            try:
                if get_prompt_service().set_active_version(prompt.prompt_name, prompt.version):
                    st.success("Prompt activated successfully!")
                    st.rerun()
                else:
                    st.error("Failed to activate prompt")
            except Exception as e:
                st.error(f"Failed to activate prompt: {e}")
