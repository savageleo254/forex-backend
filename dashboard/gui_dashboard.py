import sys
if sys.version_info >= (3, 13):
    raise RuntimeError("❌ Savage Leo does not support Python 3.13+. Downgrade to 3.11.")
import streamlit as st
import subprocess

st.title("🧠 Savage Leo – AI Audit & Fix Dashboard")

if st.button("Run LLM Batch Audit Now"):
    with st.spinner("Running batch audit..."):
        result = subprocess.run(["python", "journal/llm_batch_audit.py"], capture_output=True, text=True)
        st.code(result.stdout)

if st.button("Run Auto Fix (autonomous_run.py)"):
    with st.spinner("Running auto_fix.py..."):
        result = subprocess.run(["python", "auto_fix.py"], capture_output=True, text=True)
        st.code(result.stdout)
