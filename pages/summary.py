"""Summary page for weekly task updates."""
import streamlit as st
from src.ui.summary import render_summary

def main():
    st.title("Summary")
    render_summary()

if __name__ == "__main__":
    main()
