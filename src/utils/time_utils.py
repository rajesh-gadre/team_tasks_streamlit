from datetime import datetime
from zoneinfo import ZoneInfo

import streamlit as st


def format_user_tz(value, fmt='%Y-%m-%d %H:%M'):
    if isinstance(value, str):
        try:
            value = datetime.fromisoformat(value)
        except ValueError:
            return value
    if value.tzinfo is None:
        value = value.replace(tzinfo=datetime.utcnow().astimezone().tzinfo)
    name = st.session_state.get('userTZ') or 'UTC'
    if name == 'Z':
        name = 'UTC'
    try:
        tz = ZoneInfo(name)
    except Exception:
        tz = ZoneInfo('UTC')
    return value.astimezone(tz).strftime(fmt)
