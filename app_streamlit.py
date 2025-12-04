import os
import sys
import streamlit as st

# Setup path
ROOT = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, ROOT)

# Tambahkan semua folder ke path
folders = ['utils', 'core', 'ai', 'screener', 'ui']
for folder in folders:
    folder_path = os.path.join(ROOT, folder)
    if os.path.exists(folder_path) and folder_path not in sys.path:
        sys.path.insert(0, folder_path)

st.set_page_config(
    page_title="WarrenAI - Stock Analysis",
    page_icon="📈",
    layout="wide"
)

def main():
    st.title("📈 WarrenAI Stock Analysis Dashboard")
    st.markdown("---")
    
    try:
        from ui.screener_panel import screener_panel
        screener_panel()
    except Exception as e:
        st.error(f"Application Error: {str(e)}")
        
        # Tampilkan struktur folder untuk debugging
        with st.expander("Debug Information"):
            st.write("**Current directory:**", os.getcwd())
            st.write("**Files and folders:**")
            for item in os.listdir('.'):
                st.write(f"- {item}")

if __name__ == "__main__":
    main()
