import streamlit as st

from src.ai.prompt_service import get_prompt_service
from src.database.models import PromptStatus
from src.utils.time_utils import format_user_tz

def render_prompt_management():
    st.header('Prompt Management')
    try:
        prompts = get_prompt_service().get_all_prompts()
    except Exception as e:
        st.error(f'Error loading prompts: {e}')
        return
    if not prompts:
        st.info('No prompts found.')
        return
    names = sorted({p.prompt_name for p in prompts})
    prompt_name = st.selectbox('Select Prompt', names)
    selected = [p for p in prompts if p.prompt_name == prompt_name]
    selected.sort(key=lambda p: p.version, reverse=True)
    active_prompt = next((p for p in selected if p.status == PromptStatus.ACTIVE), None)
    with st.form(key='create_new_version'):
        st.subheader('Create new version')
        text = st.text_area('Prompt Text', value=active_prompt.text if active_prompt else selected[0].text if selected else '')
        save = st.form_submit_button('Save')
    if save:
        target = active_prompt.id if active_prompt else selected[0].id if selected else None
        if not text.strip():
            st.error('Prompt text cannot be empty')
        elif target is None:
            st.error('Prompt not found')
        else:
            try:
                if get_prompt_service().update_prompt(target, {'text': text}):
                    st.success('New version created successfully!')
                    st.rerun()
                else:
                    st.error('Failed to create new version')
            except Exception as e:
                st.error(f'Failed to create new version: {e}')
    with st.form(key='change_active_version'):
        st.subheader('Change Active version')
        options = {f"v{p.version} - {(format_user_tz(p.created_at, '%Y-%m-%d %H:%M:%S') if p.created_at else 'unknown')}": p.version for p in selected}
        current_version = active_prompt.version if active_prompt else None
        version_choice = st.selectbox('Select Version', list(options.keys()), index=list(options.values()).index(current_version) if current_version in options.values() else 0)
        update = st.form_submit_button('Update')
    if update:
        chosen_version = options.get(version_choice)
        try:
            if get_prompt_service().set_active_version(prompt_name, chosen_version):
                st.success('Prompt activated successfully!')
                st.rerun()
            else:
                st.error('Failed to activate prompt')
        except Exception as e:
            st.error(f'Failed to activate prompt: {e}')
