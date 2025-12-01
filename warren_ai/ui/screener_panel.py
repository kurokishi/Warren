import streamlit as st
import pandas as pd

try:
    from warren_ai.screener.engine import ScreenerEngine
    from warren_ai.screener.parallel_engine import ParallelScreener
except ImportError as e:
    st.error(f"Error importing screener modules: {e}")

def screener_panel():
    st.header("AI Stock Screener")

    tickers = st.text_area("Tickers (comma separated)", "BBCA.JK, TLKM.JK, ASII.JK")
    tickers = [t.strip().upper() for t in tickers.split(",") if t.strip()]
    
    use_parallel = st.checkbox("Use Parallel Mode", value=False)
    run = st.button("Run Screener")

    if not run:
        st.info("Enter tickers and click 'Run Screener' to start analysis")
        return

    if not tickers:
        st.warning("Please enter at least one ticker")
        return

    with st.spinner("Analyzing stocks..."):
        try:
            if use_parallel:
                df = ParallelScreener().run(tickers)
            else:
                df = ScreenerEngine().analyze_batch(tickers)
        except Exception as e:
            st.error(f"Analysis failed: {e}")
            return

    if df.empty:
        st.warning("No data returned from analysis.")
        return

    # Display results
    st.subheader("📊 Screening Results")
    st.dataframe(df.sort_values("FinalScore", ascending=False))

    # Score chart
    st.bar_chart(df.set_index("Ticker")["FinalScore"])

    # Detailed analysis
    st.subheader("🔍 Detailed Analysis")
    for _, row in df.iterrows():
        with st.expander(f"{row['Ticker']} — {row.get('Label', 'N/A')}"):
            
            # AI Explanation
            if "AI_Final" in row:
                st.markdown("#### AI Analysis")
                st.write(row["AI_Final"])
            
            # Confidence
            if "Confidence" in row:
                st.progress(int(row["Confidence"]) / 100)
                st.caption(f"Confidence Level: {row['Confidence']}%")
            
            # Risks
            if "Risks" in row and isinstance(row["Risks"], list):
                st.markdown("#### ⚠️ Risk Factors")
                for risk in row["Risks"]:
                    st.write(f"- {risk}")
            
            # Scenarios
            if "Scenarios" in row and isinstance(row["Scenarios"], dict):
                st.markdown("#### 🧪 Scenario Analysis")
                for scenario_name, scenario_data in row["Scenarios"].items():
                    with st.container():
                        st.write(f"**{scenario_name}**")
                        st.write(f"Impact: {scenario_data.get('impact', 'N/A')}")
                        st.caption(scenario_data.get('comment', ''))
            
            # Resilience Score
            if "ResilienceScore" in row:
                st.progress(int(row["ResilienceScore"]) / 100)
                st.caption(f"Resilience Score: {row['ResilienceScore']}/100")

    # Disclaimer
    st.divider()
    st.caption("📜 Regulatory Disclaimer")
    if not df.empty and "Disclaimer" in df.columns:
        st.write(df.iloc[0]["Disclaimer"])
    else:
        st.write("Analysis provided for educational purposes only. Invest at your own risk.")
