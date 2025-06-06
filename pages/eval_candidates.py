"""Evaluation candidates page."""
import streamlit as st
from src.ui.eval_candidates import render_eval_candidates


def main():
    st.title("Eval Candidates")
    render_eval_candidates()


if __name__ == "__main__":
    main()
