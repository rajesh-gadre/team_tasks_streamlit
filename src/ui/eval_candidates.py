"""UI for selecting evaluation candidates from AI chats."""

import streamlit as st

from src.eval.eval_input_service import get_eval_input_service
from src.database.firestore import get_client
from src.database.models import EvalStatus


def _load_ai_chats(count: int):
    return get_client().query(
        'AI_chats',
        order_by='createdAt',
        direction='DESCENDING',
        limit=count,
    )


def _render_chat_row(chat):
    cols = st.columns([4, 2, 1, 1])
    cols[0].markdown(f"**{chat.get('inputText','')}**")
    prompt = cols[1].text_input("Prompt", key=f"prompt_{chat['id']}")
    if cols[2].button("Add to Evals", key=f"add_{chat['id']}"):
        get_eval_input_service().add_from_chat(chat, prompt)
        st.success("Added to evaluation inputs")
        st.rerun()
    if cols[3].button("Details", key=f"chat_details_{chat['id']}"):
        if 'chat_details' not in st.session_state:
            st.session_state.chat_details = {}
        if chat['id'] in st.session_state.chat_details:
            del st.session_state.chat_details[chat['id']]
        else:
            st.session_state.chat_details[chat['id']] = True
        st.rerun()
    if (
        'chat_details' in st.session_state
        and chat['id'] in st.session_state.chat_details
    ):
        st.subheader("Chat Details")
        data = {k: v for k, v in chat.items() if k != 'user_id'}
        st.json(data)
    st.divider()


def _render_eval_row(ev):
    cols = st.columns([4, 1, 1])
    cols[0].markdown(f"**{ev.input_text}** - _{ev.status}_")
    toggle = EvalStatus.ARCHIVED if ev.status == EvalStatus.ACTIVE else EvalStatus.ACTIVE
    toggle_text = "Archive" if ev.status == EvalStatus.ACTIVE else "Unarchive"
    if cols[1].button(toggle_text, key=f"toggle_{ev.id}"):
        get_eval_input_service().update_status(ev.id, toggle)
        st.rerun()
    if cols[2].button("Details", key=f"ev_details_{ev.id}"):
        if 'eval_details' not in st.session_state:
            st.session_state.eval_details = {}
        if ev.id in st.session_state.eval_details:
            del st.session_state.eval_details[ev.id]
        else:
            st.session_state.eval_details[ev.id] = True
        st.rerun()
    if (
        'eval_details' in st.session_state
        and ev.id in st.session_state.eval_details
    ):
        with st.form(key=f"edit_{ev.id}"):
            input_text = st.text_area("Input", value=ev.input_text)
            response = st.text_area("Response", value=ev.response or "")
            eval_prompt = st.text_area("Eval Prompt", value=ev.eval_prompt or "")
            submit = st.form_submit_button("Save")
        if submit:
            data = {'inputText': input_text, 'evalPrompt': eval_prompt}
            if response:
                data['Response'] = response
            get_eval_input_service().update_input(ev.id, data)
            st.success("Updated")
            st.rerun()
        data = {k: v for k, v in ev.__dict__.items() if k != 'user_id'}
        st.json(data)
    st.divider()


def render_eval_candidates():
    st.header("Evaluation Candidates")
    count = int(st.number_input("Count", min_value=1, max_value=100, value=5))

    with st.expander("Recent AI Chats", expanded=True):
        chats = _load_ai_chats(count)
        if not chats:
            st.info("No chats found.")
        for chat in chats:
            _render_chat_row(chat)

    with st.expander("Evaluation Inputs", expanded=True):
        eval_inputs = get_eval_input_service().get_latest_inputs(count)
        if not eval_inputs:
            st.info("No evaluation inputs found.")
        for ev in eval_inputs:
            _render_eval_row(ev)
