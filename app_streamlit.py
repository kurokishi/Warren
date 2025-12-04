import os
import sys
import streamlit as st
import time

# Setup path
ROOT = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, ROOT)

# Add utils to path
if os.path.join(ROOT, 'utils') not in sys.path:
    sys.path.insert(0, os.path.join(ROOT, 'utils'))

st.set_page_config(
    page_title="WarrenAI Stock Analysis",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS untuk loading state
st.markdown("""
<style>
    .stSpinner > div {
        text-align: center;
    }
    .success-box {
        padding: 1rem;
        border-radius: 0.5rem;
        background-color: #d4edda;
        border: 1px solid #c3e6cb;
        color: #155724;
    }
    .error-box {
        padding: 1rem;
        border-radius: 0.5rem;
        background-color: #f8d7da;
        border: 1px solid #f5c6cb;
        color: #721c24;
    }
</style>
""", unsafe_allow_html=True)

def main():
    st.title("📈 WarrenAI – Stock Analysis Dashboard")
    
    try:
        from ui.screener_panel import screener_panel
        screener_panel()
    except ImportError as e:
        st.error(f"❌ Import Error: {e}")
        st.info("""
        **Troubleshooting Steps:**
        1. Pastikan semua folder ada: core/, ai/, screener/, ui/, utils/
        2. Pastikan semua __init__.py ada
        3. Cek struktur folder di GitHub
        """)
    except Exception as e:
        st.error(f"❌ Unexpected Error: {str(e)}")
        
        # Tampilkan info debugging
        with st.expander("Debug Information"):
            st.write(f"Python version: {sys.version}")
            st.write(f"Current directory: {os.getcwd()}")
            st.write(f"Files in directory: {os.listdir('.')}")

if __name__ == "__main__":
    main()
