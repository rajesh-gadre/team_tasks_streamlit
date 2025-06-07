"""Run evaluations against stored inputs."""
import streamlit as st
from src.ui.run_evals import render_run_evals


def main():
    st.title("Run Evals")
    render_run_evals()


if __name__ == "__main__":
    main()
