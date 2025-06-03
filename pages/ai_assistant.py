"""
AI Assistant page for the Task Management System.
"""
import streamlit as st
from src.ui.ai_chat import render_ai_chat

def main():
    st.title("AI Assistant")
    render_ai_chat()

if __name__ == "__main__":
    main()
