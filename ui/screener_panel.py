import streamlit as st
from warren_ai.screener.engine import ScreenerEngine
from warren_ai.screener.parallel_engine import ParallelScreener


def screener_panel():
    st.header("AI Stock Screener")

    tickers = st.text_area("Tickers (comma)", "BBCA,TLKM,ASII")
    tickers = [t.strip().upper() for t in tickers.split(",")]

    use_parallel = st.checkbox("Use Parallel Mode")
    run = st.button("Run Screener")

for _, row in df.iterrows():
    with st.expander(f"{row['Ticker']} — {row['Label']}"):
        st.markdown("### 🔍 AI Final Explanation")
        st.markdown(row["AI_Final"])

        with st.expander("⚙ Rule-based details"):
            st.markdown(row["AI_Rule"])

        if row["AI_LLM"]:
            with st.expander("🧠 LLM narrative"):
                st.markdown(row["AI_LLM"])

        st.dataframe(df.sort_values("FinalScore", ascending=False))
        st.bar_chart(df.set_index("Ticker")["FinalScore"])
