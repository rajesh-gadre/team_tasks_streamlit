"""UI for running evaluations on stored inputs."""

import streamlit as st

from src.ai.eval_input_service import get_eval_input_service
from src.ai.eval_service import get_eval_service
from src.ai.prompt_repository import get_prompt_repository
from src.database.models import EvalStatus


def render_run_evals():
    st.header("Run Evals")

    eval_inputs = get_eval_input_service().get_latest_inputs(100)
    active_inputs = [ev for ev in eval_inputs if ev.status == EvalStatus.ACTIVE]

    with st.expander("Evaluation Inputs", expanded=True):
        if not active_inputs:
            st.info("No evaluation inputs found.")
        for ev in active_inputs:
            st.markdown(f"- {ev.input_text}")

    repo = get_prompt_repository()
    prompts = repo.get_all_prompts()
    if not prompts:
        st.info("No prompts available.")
        return

    names = sorted({p.prompt_name for p in prompts})
    prompt_name = st.selectbox("Prompt Name", names)
    versions = sorted(
        [p.version for p in prompts if p.prompt_name == prompt_name], reverse=True
    )
    prompt_version = st.selectbox("Prompt Version", versions)

    if st.button("Run Evaluations"):
        get_eval_service().run_evals(prompt_name, int(prompt_version), active_inputs)
        st.success("Evaluations completed")
