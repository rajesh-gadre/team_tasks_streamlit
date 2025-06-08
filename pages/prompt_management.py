import streamlit as st
from src.ui.prompt_management import render_prompt_management

def main():
    st.title('Prompt Management')
    render_prompt_management()
if __name__ == '__main__':
    main()
