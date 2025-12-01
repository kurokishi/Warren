import streamlit as st
import pandas as pd

try:
    from screener.engine import ScreenerEngine
    from screener.parallel_engine import ParallelScreener
except ImportError as e:
    st.error(f"Import error in screener: {e}")

def screener_panel():
    st.header("🔍 AI Stock Screener")
    
    # Input section
    col1, col2 = st.columns([2, 1])
    with col1:
        tickers_input = st.text_area(
            "**Enter Stock Tickers**", 
            "BBCA.JK, TLKM.JK, ASII.JK, BBRI.JK",
            help="Enter comma-separated ticker symbols. For Indonesian stocks, use .JK suffix"
        )
    with col2:
        use_parallel = st.checkbox("Use Parallel Processing", value=False)
        run_analysis = st.button("🚀 Run Analysis", type="primary")

    if not run_analysis:
        st.info("👆 Enter tickers and click 'Run Analysis' to start")
        return

    # Process tickers
    tickers = [t.strip().upper() for t in tickers_input.split(",") if t.strip()]
    if not tickers:
        st.warning("Please enter at least one ticker")
        return

    # Run analysis
    with st.spinner(f"🔬 Analyzing {len(tickers)} stocks..."):
        try:
            if use_parallel:
                df = ParallelScreener().run(tickers)
            else:
                df = ScreenerEngine().analyze_batch(tickers)
        except Exception as e:
            st.error(f"Analysis failed: {str(e)}")
            return

    if df.empty:
        st.warning("No results returned. Check ticker symbols.")
        return

    # Display results
    st.success(f"✅ Analysis complete! Processed {len(df)} stocks")
    
    # Summary table
    st.subheader("📊 Results Summary")
    
    # Create display dataframe with essential columns
    display_cols = ['Ticker', 'FinalScore', 'Label', 'Confidence']
    available_cols = [col for col in display_cols if col in df.columns]
    
    display_df = df[available_cols].copy()
    st.dataframe(
        display_df.sort_values("FinalScore", ascending=False),
        use_container_width=True
    )

    # Score chart
    if 'FinalScore' in df.columns:
        st.subheader("📈 Score Comparison")
        chart_data = df[['Ticker', 'FinalScore']].set_index('Ticker')
        st.bar_chart(chart_data)

    # Detailed analysis
    st.subheader("🔍 Detailed Analysis")
    for _, row in df.iterrows():
        with st.expander(f"{row['Ticker']} - {row.get('Label', 'N/A')} (Score: {row.get('FinalScore', 0)})"):
            
            # AI Analysis
            if row.get('AI_Final'):
                st.markdown("#### 🤖 AI Analysis")
                st.write(row['AI_Final'])
            
            # Confidence
            if row.get('Confidence'):
                confidence = int(row['Confidence'])
                st.progress(confidence / 100)
                st.write(f"**Confidence Level:** {confidence}%")
            
            # Risks
            if row.get('Risks') and isinstance(row['Risks'], list):
                st.markdown("#### ⚠️ Risk Factors")
                for risk in row['Risks']:
                    st.write(f"• {risk}")
            
            # Scenarios
            if row.get('Scenarios') and isinstance(row['Scenarios'], dict):
                st.markdown("#### 🌪️ Scenario Analysis")
                for scenario, data in row['Scenarios'].items():
                    impact = data.get('impact', 0)
                    color = "🟢" if impact > 0 else "🔴" if impact < 0 else "🟡"
                    st.write(f"{color} **{scenario}:** Impact {impact} - {data.get('comment', '')}")
            
            # Resilience
            if row.get('ResilienceScore'):
                resilience = int(row['ResilienceScore'])
                st.progress(resilience / 100)
                st.write(f"**Resilience Score:** {resilience}/100")

    # Disclaimer
    st.divider()
    st.caption("📜 Regulatory Disclaimer")
    if not df.empty and 'Disclaimer' in df.columns:
        st.info(df.iloc[0]['Disclaimer'])
    else:
        st.info("Investment analysis provided for educational purposes only. Consult a financial advisor before making investment decisions.")
