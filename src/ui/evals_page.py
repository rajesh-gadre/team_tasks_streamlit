import streamlit as st
from src.ui.eval_candidates import render_eval_candidates
from src.ui.run_evals import render_run_evals

def render_evals():
    st.title('Evals')
    tabs = st.tabs(['Eval Candidates', 'Run Evals'])
    with tabs[0]:
        render_eval_candidates()
    with tabs[1]:
        render_run_evals()
