import streamlit as st
import pandas as pd
import time  # ✅ TAMBAHKAN INI

try:
    from screener.engine import ScreenerEngine
    from screener.parallel_engine import ParallelScreener
except ImportError as e:
    st.error(f"Import error in screener: {e}")

def screener_panel():
    st.header("🔍 AI Stock Screener")
    
    # Input section dengan styling lebih baik
    with st.container():
        col1, col2 = st.columns([3, 1])
        
        with col1:
            st.markdown("### 📝 Enter Stock Tickers")
            tickers_input = st.text_area(
                "Separate with commas", 
                "BBCA.JK, TLKM.JK, ASII.JK",
                help="Contoh: BBCA.JK, TLKM.JK, ASII.JK, BBRI.JK",
                label_visibility="collapsed"
            )
            
        with col2:
            st.markdown("### ⚙️ Settings")
            use_parallel = st.checkbox("Parallel Processing", value=False)
            st.markdown("---")
            run_analysis = st.button(
                "🚀 **Run Analysis**", 
                type="primary",
                use_container_width=True
            )

    if not run_analysis:
        st.info("💡 **Enter tickers above and click 'Run Analysis' to start**")
        return

    # Process tickers
    tickers = [t.strip().upper() for t in tickers_input.split(",") if t.strip()]
    
    if not tickers:
        st.warning("⚠️ Please enter at least one ticker")
        return

    # Run analysis dengan progress bar
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    status_text.text(f"🔍 Starting analysis of {len(tickers)} stocks...")
    
    try:
        if use_parallel:
            df = ParallelScreener().run(tickers)
        else:
            df = ScreenerEngine().analyze_batch(tickers)
    except Exception as e:
        st.error(f"❌ Analysis failed: {str(e)}")
        return
    
    progress_bar.progress(100)
    status_text.text("✅ Analysis complete!")
    
    time.sleep(0.5)
    progress_bar.empty()
    status_text.empty()

    if df.empty:
        st.warning("📭 No results returned. Please check your ticker symbols.")
        return

    # Display results
    success_msg = st.success(f"✅ **Analysis complete!** Processed **{len(df)}** stocks")
    
    # Score summary
    with st.container():
        st.subheader("📊 Results Summary")
        
        # Filter hanya baris yang berhasil
        if 'Label' in df.columns:
            valid_df = df[~df['Label'].isin(['ERROR', 'Failed'])]
        else:
            valid_df = df
        
        if len(valid_df) > 0:
            # Buat summary cards
            cols = st.columns(4)
            
            with cols[0]:
                if 'FinalScore' in valid_df.columns:
                    avg_score = valid_df['FinalScore'].mean()
                    st.metric("📈 Average Score", f"{avg_score:.1f}")
                else:
                    st.metric("📈 Average Score", "N/A")
            
            with cols[1]:
                if 'Label' in valid_df.columns:
                    buy_count = len(valid_df[valid_df['Label'].str.contains('BUY', case=False)])
                    st.metric("🟢 Buy Signals", buy_count)
                else:
                    st.metric("🟢 Buy Signals", 0)
            
            with cols[2]:
                if 'Label' in valid_df.columns:
                    hold_count = len(valid_df[valid_df['Label'] == 'HOLD'])
                    st.metric("🟡 HOLD", hold_count)
                else:
                    st.metric("🟡 HOLD", 0)
            
            with cols[3]:
                if 'Label' in valid_df.columns:
                    avoid_count = len(valid_df[valid_df['Label'] == 'AVOID'])
                    st.metric("🔴 AVOID", avoid_count)
                else:
                    st.metric("🔴 AVOID", 0)
        
        # Results table
        st.markdown("#### 📋 Detailed Results")
        
        # Pilih kolom untuk ditampilkan
        display_cols = ['Ticker', 'FinalScore', 'Label', 'Confidence', 'ResilienceScore']
        available_cols = [col for col in display_cols if col in df.columns]
        
        if available_cols:
            display_df = df[available_cols].copy()
            
            # Format angka
            if 'FinalScore' in display_df.columns:
                display_df['FinalScore'] = display_df['FinalScore'].round(1)
            
            if 'Confidence' in display_df.columns:
                display_df['Confidence'] = display_df['Confidence'].astype(int).astype(str) + '%'
            
            if 'ResilienceScore' in display_df.columns:
                display_df['ResilienceScore'] = display_df['ResilienceScore'].astype(int).astype(str) + '/100'
            
            # Sort by score
            if 'FinalScore' in display_df.columns:
                display_df = display_df.sort_values('FinalScore', ascending=False)
            
            # Tampilkan table
            st.dataframe(
                display_df,
                use_container_width=True,
                hide_index=True
            )
            
            # Score chart
            if 'FinalScore' in df.columns:
                st.markdown("#### 📈 Score Comparison")
                chart_data = df[['Ticker', 'FinalScore']].set_index('Ticker')
                if 'FinalScore' in df.columns:
                    chart_data = chart_data.sort_values('FinalScore', ascending=False)
                st.bar_chart(chart_data)

    # Detailed analysis untuk setiap stock
    st.subheader("🔍 Detailed Analysis")
    
    for idx, row in df.iterrows():
        ticker = row['Ticker'] if 'Ticker' in row else f"Stock_{idx}"
        label = row.get('Label', 'N/A')
        score = row.get('FinalScore', 0)
        
        # Tentukan warna berdasarkan label
        if 'BUY' in str(label):
            color = "🟢"
        elif label == 'HOLD':
            color = "🟡"
        elif label == 'AVOID':
            color = "🔴"
        else:
            color = "⚪"
        
        with st.expander(f"{color} **{ticker}** - {label} (Score: {score})"):
            
            # Tampilkan error jika ada
            if 'Error' in row and row['Error']:
                st.error(f"**Error:** {row['Error']}")
                continue
            
            # AI Analysis
            if row.get('AI_Final'):
                st.markdown("##### 🤖 AI Analysis")
                st.info(row['AI_Final'])
            
            # Confidence
            if row.get('Confidence'):
                confidence = int(row['Confidence'])
                st.markdown(f"##### 📊 Confidence: **{confidence}%**")
                st.progress(confidence / 100, text="")
            
            # Fundamental Data
            st.markdown("##### 📊 Fundamental Data")
            fund_cols = st.columns(3)
            
            with fund_cols[0]:
                if row.get('PER'):
                    st.metric("PER", f"{row['PER']:.1f}")
                else:
                    st.metric("PER", "N/A")
            
            with fund_cols[1]:
                if row.get('PBV'):
                    st.metric("PBV", f"{row['PBV']:.2f}")
                else:
                    st.metric("PBV", "N/A")
            
            with fund_cols[2]:
                if row.get('ROE'):
                    st.metric("ROE", f"{row['ROE']:.1%}")
                else:
                    st.metric("ROE", "N/A")
            
            # Technical Data
            st.markdown("##### 📈 Technical Data")
            tech_cols = st.columns(2)
            
            with tech_cols[0]:
                if row.get('RSI'):
                    st.metric("RSI", f"{row['RSI']:.1f}")
                else:
                    st.metric("RSI", "N/A")
            
            with tech_cols[1]:
                if row.get('MACD'):
                    st.metric("MACD", f"{row['MACD']:.4f}")
                else:
                    st.metric("MACD", "N/A")
            
            # Risks
            if row.get('Risks') and isinstance(row['Risks'], list) and len(row['Risks']) > 0:
                st.markdown("##### ⚠️ Risk Factors")
                for risk in row['Risks']:
                    st.warning(risk)
            
            # Scenarios
            if row.get('Scenarios') and isinstance(row['Scenarios'], dict):
                st.markdown("##### 🌪️ Scenario Analysis")
                
                for scenario_name, scenario_data in row['Scenarios'].items():
                    impact = scenario_data.get('impact', 0)
                    
                    # Tentukan warna impact
                    if impact > 0:
                        impact_color = "success"
                        impact_icon = "📈"
                    elif impact < 0:
                        impact_color = "error"
                        impact_icon = "📉"
                    else:
                        impact_color = "warning"
                        impact_icon = "➖"
                    
                    with st.container():
                        st.markdown(f"**{impact_icon} {scenario_name}**")
                        st.caption(f"Impact: **{impact}**")
                        st.caption(scenario_data.get('comment', ''))
            
            # Resilience Score
            if row.get('ResilienceScore'):
                resilience = int(row['ResilienceScore'])
                st.markdown(f"##### 🛡️ Resilience Score: **{resilience}/100**")
                st.progress(resilience / 100, text="")
                
                if resilience > 70:
                    st.success("Tingkat ketahanan tinggi terhadap tekanan pasar")
                elif resilience > 40:
                    st.info("Tingkat ketahanan sedang")
                else:
                    st.warning("Tingkat ketahanan rendah")

    # Disclaimer section
    st.divider()
    
    with st.container():
        st.markdown("##### 📜 Regulatory Disclaimer")
        
        if not df.empty and 'Disclaimer' in df.columns and pd.notna(df.iloc[0]['Disclaimer']):
            disclaimer_text = df.iloc[0]['Disclaimer']
        else:
            disclaimer_text = """Analisis ini dihasilkan oleh sistem AI sebagai alat bantu riset. Bukan merupakan rekomendasi investasi, ajakan membeli atau menjual efek tertentu. Investor bertanggung jawab penuh atas setiap keputusan investasi yang diambil. Investasi saham mengandung risiko, termasuk kemungkinan kehilangan sebagian atau seluruh modal."""
        
        st.info(disclaimer_text)
        
    # Debug info kecil di footer
    with st.expander("🔧 Debug Info"):
        st.write(f"Total stocks analyzed: {len(df)}")
        st.write(f"Columns available: {list(df.columns)}")
        if 'AnalysisTime' in df.columns:
            st.write(f"Average analysis time: {df['AnalysisTime'].mean():.2f} seconds")
