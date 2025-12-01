import os
import sys
import streamlit as st

# Tambahkan path yang benar
ROOT = os.path.abspath(os.path.dirname(__file__))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

# Import yang benar
try:
    from warren_ai.ui.screener_panel import screener_panel
except ImportError as e:
    st.error(f"Import error: {e}")
    st.stop()

st.set_page_config(layout="wide")
st.title("WarrenAI – Stock Analysis Dashboard")

screener_panel()
