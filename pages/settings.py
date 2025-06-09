import streamlit as st
from src.ui.settings import render_settings

def main():
    st.title('Settings')
    render_settings()

if __name__ == '__main__':
    main()
