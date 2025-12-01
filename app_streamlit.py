import os
import sys
import streamlit as st

# Setup path
ROOT = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, ROOT)

try:
    from ui.screener_panel import screener_panel
except ImportError as e:
    st.error(f"Import Error: {e}")
    st.stop()

st.set_page_config(
    page_title="WarrenAI Stock Analysis",
    page_icon="📈",
    layout="wide"
)

st.title("📈 WarrenAI – Stock Analysis Dashboard")
screener_panel()
