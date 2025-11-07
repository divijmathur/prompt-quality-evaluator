# app/layout.py
import streamlit as st

def render_header():
    st.title("🔍 LLM Prompt Quality Evaluator")
    st.markdown("Compare clarity, factuality, and style across model responses.")