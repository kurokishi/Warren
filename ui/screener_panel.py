import streamlit as st
from warren_ai.screener.engine import ScreenerEngine
from warren_ai.screener.parallel_engine import ParallelScreener


def screener_panel():
    st.header("AI Stock Screener")

    tickers = st.text_area("Tickers (comma)", "BBCA,TLKM,ASII")
    tickers = [t.strip().upper() for t in tickers.split(",") if t.strip()]

    use_parallel = st.checkbox("Use Parallel Mode")
    run = st.button("Run Screener")

    if not run:
        return

    with st.spinner("Processing..."):
        if use_parallel:
            df = ParallelScreener().run(tickers)
        else:
            df = ScreenerEngine().analyze_batch(tickers)

    if df.empty:
        st.warning("No data returned.")
        return

    # === MAIN TABLE ===
    st.subheader("Screener Results")
    st.dataframe(df.sort_values("FinalScore", ascending=False))

    st.bar_chart(df.set_index("Ticker")["FinalScore"])

    # === DETAIL PER STOCK ===
    st.subheader("AI Analysis Detail")

    for _, row in df.iterrows():
        with st.expander(f"{row['Ticker']} — {row['Label']}"):

            # --- AI Explanation ---
            st.markdown("### 🔍 AI Final Explanation")
            st.markdown(row.get("AI_Final", "No explanation"))

            # --- Confidence ---
            if "Confidence" in row:
                st.progress(int(row["Confidence"]))
                st.caption(f"Confidence: {row['Confidence']}%")

            # --- Risk ---
            if "Risks" in row:
                st.markdown("### ⚠️ Risk Disclosure")
                for r in row["Risks"]:
                    st.markdown(f"- {r}")

            # --- Scenario & Stress ---
            if "Scenarios" in row:
                st.markdown("### 🧪 Scenario & Stress Analysis")
                for name, sc in row["Scenarios"].items():
                    st.markdown(f"**{name}**")
                    st.write(f"Impact Score: {sc['impact']}")
                    st.caption(sc['comment'])

                st.progress(int(row["ResilienceScore"]))
                st.caption(f"Resilience Score: {row['ResilienceScore']}/100")

            # --- Debug / Transparency ---
            with st.expander("⚙ Rule-Based Explanation"):
                st.markdown(row.get("AI_Rule", "-"))

            if row.get("AI_LLM"):
                with st.expander("🧠 LLM Narrative"):
                    st.markdown(row["AI_LLM"])
