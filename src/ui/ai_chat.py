import json
import logging
import traceback
import streamlit as st
from typing import Dict, Any
from src.ai.llm_service import get_llm_service, TaskChanges
from src.database.firestore import get_client
logger = logging.getLogger(__name__)

def __collect_feedback(chat_id: str, resp: TaskChanges) -> bool:
    feedback_key = f'feedback_submitted_{chat_id}'
    logger.info(f'\n\n\nCollecting feedback for chat_id {chat_id}, resp: {resp}')
    if st.session_state.get(feedback_key):
        return True
    logger.info(f'Before ST.FORM in collecting feedback: chat_id={chat_id!r}, resp={resp!r}')
    with st.form(f'feedback_form_{chat_id}'):
        st.subheader('New Tasks')
        for t in resp.new_tasks:
            st.json(getattr(t, 'model_dump', t.dict)(exclude_none=True))
        st.subheader('Modified Tasks')
        for t in resp.modified_tasks:
            st.json(getattr(t, 'model_dump', t.dict)(exclude_none=True))
        rating = st.radio('Are these updates correct?', ('👍', '👎'), key=f'rating_{chat_id}', horizontal=True)
        text = st.text_area('Additional feedback', key=f'text_{chat_id}')
        submit = st.form_submit_button('Submit')
        cancel = st.form_submit_button('Cancel')
        if submit:
            logger.info(f'Feedback submitted for chat_id {chat_id}')
            st.session_state[feedback_key] = True
            get_client().update('AI_chats', chat_id, {'feedbackRating': rating, 'feedbackText': text})
            st.success('Feedback recorded')
            return True
        if cancel:
            logger.info(f'Feedback cancelled for chat_id {chat_id}')
            st.session_state[feedback_key] = True
            return True
    return False

def _display_response(resp: TaskChanges):
    st.subheader('Response')
    last = st.session_state.get('ai_last_input')
    if last:
        st.code(last)
    st.json(getattr(resp, 'model_dump', resp.dict)(exclude_none=True))

def _process_chat(user_id: str):
    try:
        ai_input_with_id = st.session_state.get('ai_input_with_id', f"{st.session_state.ai_input}\n\nuser_id: {user_id}")
        result = get_llm_service().process_chat(user_id, ai_input_with_id)
        if result:
            st.session_state.ai_response = result.get('response')
            st.session_state.chat_id = result.get('chat_id')
            st.session_state.ai_input = ''
            st.session_state.ai_processing = False
            st.session_state.ai_input_with_id = ''
            st.rerun()
    except Exception as e:
        logger.error(f'Error processing AI chat: {str(e)}')
        st.error(f'Error processing your question: {str(e)}')
        st.session_state.ai_processing = False
        traceback.print_exc()

def _main_tab(user_id: str):
    if st.session_state.ai_processing:
        _process_chat(user_id)
    with st.form(key='ai_chat_form'):
        ai_input = st.text_area('Your request', value=st.session_state.ai_input, height=100)
        submit_button = st.form_submit_button('Submit')
    if submit_button and ai_input.strip():
        st.session_state.ai_input = ai_input
        st.session_state.ai_input_with_id = f"{ai_input}\n\nuser_id: {user_id}"
        st.session_state.ai_last_input = ai_input
        st.session_state.ai_processing = True
        st.rerun()
    if st.session_state.ai_response:
        _display_response(st.session_state.ai_response)

def _load_chats(user_id: str):
    return get_client().query('AI_chats', filters=[('user_id', '==', user_id)], order_by='createdAt', direction='DESCENDING', limit=20)

def _feedback_tab(user_id: str):
    chats = _load_chats(user_id)
    if not chats:
        st.info('No chats found.')
    for chat in chats:
        text = chat.get('inputText', '').split('user_id')[0].rstrip('\n')
        st.markdown(f'**{text}**')
        if st.button('Feedback', key=f"fb_{chat['id']}"):
            st.session_state.setdefault('fb_open', {})
            st.session_state.fb_open[chat['id']] = not st.session_state.fb_open.get(chat['id'])
            st.rerun()
        if st.session_state.get('fb_open', {}).get(chat['id']):
            data = chat.get('Response')
            if data:
                if isinstance(data, str):
                    data = json.loads(data)
                resp = TaskChanges(**data)
                __collect_feedback(chat['id'], resp)
        st.divider()

def render_ai_chat():
    st.header('AI Assistant')
    user_id = st.session_state.user.get('email')
    if 'ai_input' not in st.session_state:
        st.session_state.ai_input = ''
    if 'ai_response' not in st.session_state:
        st.session_state.ai_response = None
    if 'ai_processing' not in st.session_state:
        st.session_state.ai_processing = False
    st.markdown('\n    Talk with the AI assistant for help creating and/or updating your tasks. \n    ')
    tabs = st.tabs(['Main', 'Feedback'])
    with tabs[0]:
        _main_tab(user_id)
    with tabs[1]:
        _feedback_tab(user_id)
