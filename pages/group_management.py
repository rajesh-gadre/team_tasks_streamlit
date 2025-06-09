import streamlit as st
from src.ui.group_management import render_group_management


def main():
    st.title('Group Management')
    render_group_management()


if __name__ == '__main__':
    main()
