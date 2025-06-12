import streamlit as st
from src.ai.prompt_service import get_prompt_service
from src.database.models import PromptStatus
from src.utils.time_utils import format_user_tz


def _save_prompt(text, target):
    if not text.strip():
        st.error('Prompt text cannot be empty')
        return
    if target is None:
        st.error('Prompt not found')
        return
    try:
        if get_prompt_service().update_prompt(target, {'text': text}):
            st.success('New version created successfully!')
            st.rerun()
        else:
            st.error('Failed to create new version')
    except Exception as e:
        st.error(f'Failed to create new version: {e}')


def _create_version_form(text, target):
    with st.form(key='create_new_version'):
        st.subheader('Create new version')
        value = st.text_area('Prompt Text', value=text)
        save = st.form_submit_button('Save')
    if save:
        _save_prompt(value, target)


def _upload_section(target):
    file = st.file_uploader('Upload Prompt File', type=['txt'])
    if file and st.button('Upload'):
        _save_prompt(file.getvalue().decode('utf-8'), target)


def _change_active_version_form(selected, active, name):
    with st.form(key='change_active_version'):
        st.subheader('Change Active version')
        options = {
            f"v{p.version} - {(format_user_tz(p.created_at, '%Y-%m-%d %H:%M:%S') if p.created_at else 'unknown')}": p.version
            for p in selected
        }
        current = active.version if active else None
        idx = list(options.values()).index(current) if current in options.values() else 0
        choice = st.selectbox('Select Version', list(options.keys()), index=idx)
        update = st.form_submit_button('Update')
    if update:
        version = options.get(choice)
        try:
            if get_prompt_service().set_active_version(name, version):
                st.success('Prompt activated successfully!')
                st.rerun()
            else:
                st.error('Failed to activate prompt')
        except Exception as e:
            st.error(f'Failed to activate prompt: {e}')


def _download_section(name, active):
    if active:
        st.download_button(
            'Download Active Prompt',
            active.text,
            file_name=f'{name}_v{active.version}.txt',
        )


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
    active = next((p for p in selected if p.status == PromptStatus.ACTIVE), None)
    target = active.id if active else selected[0].id if selected else None
    text = active.text if active else selected[0].text if selected else ''
    _create_version_form(text, target)
    _upload_section(target)
    _change_active_version_form(selected, active, prompt_name)
    _download_section(prompt_name, active)
