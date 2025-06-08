import subprocess

import streamlit as st


def render_run_tests():
    st.header('Run Tests')
    if st.button('Run Tests with Coverage'):
        with st.spinner('Running tests...'):
            result = subprocess.run(
                ['pytest', '--cov=src', '--cov=tests', '--cov-report=term-missing'],
                capture_output=True,
                text=True,
            )
        st.session_state.test_output = result.stdout + result.stderr
        st.session_state.test_returncode = result.returncode
        st.rerun()
    if getattr(st.session_state, 'test_output', None) is not None:
        st.code(st.session_state.test_output)
        if st.session_state.test_returncode == 0:
            st.success('Tests passed')
        else:
            st.error('Tests failed')
