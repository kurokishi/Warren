import streamlit as st
import pandas as pd
import time
import plotly.graph_objects as go
from plotly.subplots import make_subplots

try:
    from screener.engine import ScreenerEngine
    from screener.parallel_engine import ParallelScreener
    from ai.peer_comparator import PeerComparator  # ✅ New
except ImportError as e:
    st.error(f"Import error in screener: {e}")

def screener_panel():
    st.header("🔍 AI Stock Screener - Enhanced")
    
    # Tab interface untuk fitur-fitur baru
    tab1, tab2, tab3 = st.tabs(["📊 Stock Analysis", "🤖 AI Predictions", "📈 Peer Comparison"])
    
    with tab1:
        render_basic_analysis()
    
    with tab2:
        render_ai_predictions()
    
    with tab3:
        render_peer_comparison()

def render_basic_analysis():
    """Render basic stock analysis interface"""
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
            enable_ai_features = st.checkbox("Enable AI Features", value=True)
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
    st.success(f"✅ **Analysis complete!** Processed **{len(df)}** stocks")
    
    # Tampilkan enhanced results
    display_enhanced_results(df)

def render_ai_predictions():
    """Render AI prediction features"""
    st.markdown("## 🤖 AI Price Predictions")
    
    ticker = st.text_input("Enter ticker for prediction:", "BBCA.JK").upper()
    
    col1, col2 = st.columns(2)
    with col1:
        prediction_days = st.slider("Prediction days:", 3, 10, 5)
    with col2:
        run_prediction = st.button("🔮 Predict Price", type="primary")
    
    if run_prediction and ticker:
        with st.spinner("Running AI prediction..."):
            try:
                from core.stock import StockAnalyzer
                analyzer = StockAnalyzer(ticker)
                result = analyzer.analyze()
                
                if "PricePrediction" in result:
                    display_price_prediction(result["PricePrediction"], ticker)
                else:
                    st.warning("Price prediction not available")
                    
            except Exception as e:
                st.error(f"Prediction failed: {str(e)}")

def render_peer_comparison():
    """Render peer comparison features"""
    st.markdown("## 📈 Peer Comparison")
    
    main_ticker = st.text_input("Main ticker:", "BBCA.JK").upper()
    
    if st.button("🔄 Compare with Peers", type="primary"):
        with st.spinner("Analyzing peers..."):
            try:
                from core.stock import StockAnalyzer
                from ai.peer_comparator import PeerComparator
                
                # Analyze main ticker
                analyzer = StockAnalyzer(main_ticker)
                result = analyzer.analyze()
                
                # Get comparison data
                comparator = PeerComparator()
                comparison_df = comparator.create_comparison_data(main_ticker, result)
                
                # Display comparison
                st.dataframe(comparison_df, use_container_width=True)
                
                # Radar chart
                radar_fig = comparator.create_radar_chart(comparison_df)
                if radar_fig:
                    st.plotly_chart(radar_fig, use_container_width=True)
                
                # Insights
                insights = comparator.get_comparison_insights(comparison_df)
                st.info(insights)
                
                # News sentiment comparison
                st.markdown("### 📰 News Sentiment")
                if "NewsSentiment" in result:
                    display_news_sentiment(result["NewsSentiment"])
                
            except Exception as e:
                st.error(f"Comparison failed: {str(e)}")

def display_enhanced_results(df):
    """Display enhanced analysis results"""
    # Results table
    st.subheader("📊 Analysis Results")
    
    # Select columns to display
    display_cols = ['Ticker', 'FinalScore', 'Label', 'Confidence', 'ResilienceScore']
    if all(col in df.columns for col in display_cols):
        display_df = df[display_cols].copy()
        
        # Format numbers
        display_df['FinalScore'] = display_df['FinalScore'].round(1)
        display_df['Confidence'] = display_df['Confidence'].astype(int).astype(str) + '%'
        display_df['ResilienceScore'] = display_df['ResilienceScore'].astype(int).astype(str) + '/100'
        
        st.dataframe(
            display_df.sort_values('FinalScore', ascending=False),
            use_container_width=True,
            hide_index=True
        )
    
    # Detailed analysis for each stock
    for idx, row in df.iterrows():
        if row.get('Label') == 'ERROR':
            continue
            
        with st.expander(f"🔍 {row['Ticker']} - {row.get('Label', 'N/A')} (Score: {row.get('FinalScore', 0)})"):
            render_stock_details(row)

def render_stock_details(row):
    """Render detailed stock analysis"""
    # Price prediction
    if "PricePrediction" in row and isinstance(row["PricePrediction"], dict):
        if "error" not in row["PricePrediction"]:
            display_price_prediction(row["PricePrediction"], row['Ticker'])
        st.divider()
    
    # News sentiment
    if "NewsSentiment" in row and isinstance(row["NewsSentiment"], dict):
        if "error" not in row["NewsSentiment"]:
            display_news_sentiment(row["NewsSentiment"])
        st.divider()
    
    # Peer insights
    if "PeerInsights" in row and row["PeerInsights"]:
        st.markdown("#### 👥 Peer Comparison Insights")
        st.info(row["PeerInsights"])
        st.divider()
    
    # Existing analysis
    render_existing_analysis(row)

def display_price_prediction(prediction, ticker):
    """Display CONSERVATIVE price prediction with proper warnings"""
    
    if "error" in prediction:
        st.warning(f"Prediksi harga untuk {ticker} tidak tersedia")
        return
    
    st.markdown(f"#### 🔮 Analisis Teknis & Prediksi {ticker}")
    
    # WARNING BANNER
    st.warning("""
    ⚠️ **PERINGATAN PENTING:** 
    Prediksi harga bersifat probabilistik dan tidak akurat. 
    **JANGAN** gunakan sebagai satu-satunya dasar keputusan investasi.
    Selalu lakukan analisis independen dan konsultasi dengan penasihat keuangan.
    """)
    
    # Current price and realistic range
    col1, col2, col3 = st.columns(3)
    
    with col1:
        current = prediction.get('current_price', 0)
        st.metric(
            "Harga Saat Ini", 
            f"Rp {current:,.0f}",
            help="Harga penutupan terakhir"
        )
    
    with col2:
        range_info = prediction.get('realistic_range', {})
        optimistic = range_info.get('optimistic', current)
        st.metric(
            "Range Optimistis (5 hari)", 
            f"Rp {optimistic:,.0f}",
            delta=f"+{(optimistic/current-1)*100:.1f}%",
            delta_color="off"
        )
    
    with col3:
        pessimistic = range_info.get('pessimistic', current)
        st.metric(
            "Range Pesimistis (5 hari)", 
            f"Rp {pessimistic:,.0f}",
            delta=f"-{(1-pessimistic/current)*100:.1f}%",
            delta_color="off"
        )
    
    # Volatility and Confidence
    col1, col2 = st.columns(2)
    
    with col1:
        volatility = prediction.get('volatility_pct', 0)
        st.metric(
            "Volatilitas Historis", 
            f"{volatility:.1f}%",
            help="Standar deviasi pergerakan harian"
        )
    
    with col2:
        confidence = prediction.get('confidence', 0)
        st.metric(
            "Tingkat Kepercayaan", 
            f"{confidence:.0f}%",
            help="Seberapa yakin sistem dengan prediksi ini"
        )
    
    # Trading Scenarios (MORE USEFUL than single prediction)
    if 'trading_scenarios' in prediction:
        st.markdown("##### 📊 Skenario Trading yang Mungkin")
        
        scenarios = prediction['trading_scenarios']
        
        if 'conservative_advice' in scenarios:
            # When data is limited
            advice = scenarios['conservative_advice']
            st.info(f"**{advice['message']}**")
            st.write(f"**Rekomendasi:** {advice['recommendation']}")
            st.write(f"**Tindakan:** {advice['suggested_action']}")
            st.write(f"**Tingkat Risiko:** {advice['risk_level']}")
        else:
            # Display multiple scenarios
            for scenario_name, scenario_data in scenarios.items():
                with st.expander(f"📈 {scenario_name.replace('_', ' ').title()} ({scenario_data.get('probability', 'N/A')})"):
                    st.write(f"**Deskripsi:** {scenario_data.get('description', '')}")
                    
                    if 'target' in scenario_data:
                        st.write(f"**Target Price:** Rp {scenario_data['target']:,.0f}")
                    
                    if 'stop_loss' in scenario_data:
                        st.write(f"**Stop Loss:** Rp {scenario_data['stop_loss']:,.0f}")
                    
                    if 'condition' in scenario_data:
                        st.write(f"**Kondisi Trigger:** {scenario_data['condition']}")
                    
                    st.write(f"**Tingkat Risiko:** {scenario_data.get('risk', 'N/A')}")
    
    # Support & Resistance Levels
    if 'support_resistance' in prediction:
        sr = prediction['support_resistance']
        st.markdown("##### 📍 Level Support & Resistance")
        
        col1, col2 = st.columns(2)
        
        with col1:
            if 'recent_high' in sr:
                st.metric("Resistance (High 20H)", f"Rp {sr['recent_high']:,.0f}")
        
        with col2:
            if 'recent_low' in sr:
                st.metric("Support (Low 20H)", f"Rp {sr['recent_low']:,.0f}")
        
        if 'psychological_levels' in sr and sr['psychological_levels']:
            st.write("**Level Psikologis Terdekat:**")
            for level in sr['psychological_levels']:
                diff_pct = (level - current) / current * 100
                st.write(f"- Rp {level:,.0f} ({diff_pct:+.1f}%)")
    
    # Bollinger Bands
    if 'bollinger_bands' in prediction and prediction['bollinger_bands']:
        bb = prediction['bollinger_bands']
        st.markdown("##### 📊 Bollinger Bands Analysis")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Upper Band", f"Rp {bb.get('upper', 0):,.0f}")
        
        with col2:
            st.metric("Middle (MA 20)", f"Rp {bb.get('middle', 0):,.0f}")
        
        with col3:
            st.metric("Lower Band", f"Rp {bb.get('lower', 0):,.0f}")
        
        width = bb.get('width_pct', 0)
        if width < 10:
            st.info(f"📉 **Bandwidth {width:.1f}%** - Volatilitas rendah, kemungkinan konsolidasi")
        elif width > 20:
            st.warning(f"📈 **Bandwidth {width:.1f}%** - Volatilitas tinggi, kemungkinan breakout")
    
    # Disclaimer Section
    st.markdown("---")
    st.caption("""
    **Catatan Penting:** 
    1. Prediksi berdasarkan data historis dan pola statistik
    2. Tidak memperhitungkan faktor fundamental mendadak (earnings surprise, news, dll)
    3. Pasar saham Indonesia memiliki karakteristik unik yang mungkin tidak tercermin dalam model
    4. Selalu gunakan stop loss dan risk management yang ketat
    """)

def display_news_sentiment(news_data):
    """Display news sentiment analysis"""
    st.markdown("#### 📰 News Sentiment Analysis")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        sentiment = news_data.get('sentiment', 'neutral')
        sentiment_color = {
            'positive': '🟢',
            'negative': '🔴', 
            'neutral': '🟡'
        }.get(sentiment, '⚪')
        st.metric("Overall Sentiment", f"{sentiment_color} {sentiment.upper()}")
    
    with col2:
        st.metric("Total News", news_data.get('total_news', 0))
    
    with col3:
        score = news_data.get('avg_score', 0)
        st.metric("Sentiment Score", f"{score:.2f}")
    
    # News breakdown
    if 'positive_count' in news_data:
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Positive", news_data['positive_count'])
        with col2:
            st.metric("Negative", news_data['negative_count'])
        with col3:
            st.metric("Neutral", news_data['neutral_count'])
    
    # Latest news
    if 'latest_news' in news_data and news_data['latest_news']:
        st.markdown("##### Recent Headlines:")
        for news in news_data['latest_news'][:3]:
            sentiment_icon = "🟢" if news['sentiment'] == 'positive' else "🔴" if news['sentiment'] == 'negative' else "🟡"
            st.write(f"{sentiment_icon} **{news['title']}**")
            st.caption(f"📅 {news['date']} | Score: {news['score']:.2f}")
    
    if 'recommendation' in news_data:
        st.info(f"**Insight:** {news_data['recommendation']}")

def render_existing_analysis(row):
    """Render existing analysis components"""
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
    
    with fund_cols[1]:
        if row.get('PBV'):
            st.metric("PBV", f"{row['PBV']:.2f}")
    
    with fund_cols[2]:
        if row.get('ROE'):
            st.metric("ROE", f"{row['ROE']:.1%}")
    
    # Technical Data
    st.markdown("##### 📈 Technical Data")
    tech_cols = st.columns(2)
    
    with tech_cols[0]:
        if row.get('RSI'):
            st.metric("RSI", f"{row['RSI']:.1f}")
    
    with tech_cols[1]:
        if row.get('MACD'):
            st.metric("MACD", f"{row['MACD']:.4f}")
    
    # Risks
    if row.get('Risks') and isinstance(row['Risks'], list) and len(row['Risks']) > 0:
        st.markdown("##### ⚠️ Risk Factors")
        for risk in row['Risks']:
            st.warning(risk)
    
    # AI Explanation
    if row.get('AI_Final'):
        st.markdown("##### 🤖 AI Analysis")
        st.info(row['AI_Final'])
