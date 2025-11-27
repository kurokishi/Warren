import os, sys
import streamlit as st

ROOT = os.path.abspath(os.path.dirname(__file__))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from ui.screener_panel import screener_panel

st.set_page_config(layout="wide")
st.title("WarrenAI – Stock Analysis Dashboard")

screener_panel()
