"""Changelog page utilities."""
from pathlib import Path
import streamlit as st


def render_changelog():
    """Display the contents of documentation/ChangeLog.md."""
    root = Path(__file__).resolve().parents[2]
    changelog_file = root / "documentation" / "ChangeLog.md"
    if not changelog_file.exists():
        st.error("Changelog file not found.")
        return
    st.markdown(changelog_file.read_text())
