import streamlit as st
from warren_ai.screener.engine import ScreenerEngine
from warren_ai.screener.parallel_engine import ParallelScreener


def screener_panel():
    st.header("AI Stock Screener")

    tickers = st.text_area("Tickers (comma)", "BBCA,TLKM,ASII")
    tickers = [t.strip().upper() for t in tickers.split(",")]

    use_parallel = st.checkbox("Use Parallel Mode")
    run = st.button("Run Screener")

    if run:
        with st.spinner("Processing..."):
            if use_parallel:
                df = ParallelScreener().run(tickers)
            else:
                df = ScreenerEngine().analyze_batch(tickers)

        st.dataframe(df.sort_values("FinalScore", ascending=False))
        st.bar_chart(df.set_index("Ticker")["FinalScore"])
