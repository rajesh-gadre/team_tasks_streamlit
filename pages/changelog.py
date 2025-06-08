import streamlit as st
from src.ui.changelog import render_changelog

def main():
    st.title('ChangeLog')
    render_changelog()
if __name__ == '__main__':
    main()
