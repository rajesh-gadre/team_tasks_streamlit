import os
from datetime import datetime, timedelta

import streamlit as st
from langchain_community.chat_models import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage

from src.tasks.task_service import get_task_service
from src.utils.time_utils import format_user_tz

def render_summary():
    st.header('Weekly Summary')
    user_id = st.session_state.user.get('email')
    tasks = get_task_service().get_all_tasks_for_user(user_id)
    one_week_ago = datetime.now(datetime.utcnow().astimezone().tzinfo) - timedelta(days=7)
    recent_updates = []
    for task in tasks:
        for update in task.updates or []:
            ts = update.get('timestamp')
            if isinstance(ts, str):
                try:
                    ts = datetime.fromisoformat(ts)
                    if ts.tzinfo is None:
                        ts = ts.replace(tzinfo=datetime.utcnow().astimezone().tzinfo)
                except ValueError:
                    continue
            if isinstance(ts, datetime) and ts >= one_week_ago:
                recent_updates.append((ts, task.title, update.get('updateText')))
    if not recent_updates:
        st.info('No task updates in the last week.')
        return
    recent_updates.sort(key=lambda x: x[0], reverse=True)
    summary = _summarize_updates(recent_updates)
    if summary:
        for line in summary.split('\n'):
            clean_line = line.lstrip('- ').strip()
            if clean_line:
                st.markdown(f'- {clean_line}')
    else:
        st.write('Here are the latest updates:')
        for ts, title, text in recent_updates[:5]:
            st.markdown(f"- **{format_user_tz(ts, '%Y-%m-%d')}**: {text} - *{title}*")

def _summarize_updates(updates):
    api_key = os.environ.get('OPENAI_API_KEY')
    if not api_key:
        return None
    try:
        chat = ChatOpenAI(api_key=api_key, model=os.environ.get('OPENAI_MODEL', 'gpt-4.1-mini'), temperature=0)
        updates_text = '\n'.join((f"- {format_user_tz(ts, '%Y-%m-%d')}: {text} ({title})" for ts, title, text in updates))
        prompt = f'Summarize the following task updates in 3-5 bullet points:\n{updates_text}'
        messages = [SystemMessage(content='You are a helpful assistant that summarizes task updates.'), HumanMessage(content=prompt)]
        response = chat.invoke(messages)
        return response.content.strip()
    except Exception:
        return None
