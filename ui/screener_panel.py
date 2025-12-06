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
    """Display price prediction results"""
    st.markdown(f"#### 🔮 Price Prediction for {ticker}")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric(
            "Current Price", 
            f"Rp {prediction.get('current_price', 0):,.0f}",
            delta=f"{prediction.get('potential_change_pct', 0):+.2f}%"
        )
    
    with col2:
        trend = prediction.get('trend', 'neutral')
        trend_icon = "📈" if trend == "bullish" else "📉" if trend == "bearish" else "➖"
        st.metric(
            "Next Day", 
            f"Rp {prediction.get('next_day_prediction', 0):,.0f}",
            delta=trend_icon
        )
    
    with col3:
        confidence = prediction.get('confidence', 50)
        st.metric("Confidence", f"{confidence}%")
    
    # Prediction chart
    if 'predictions' in prediction and len(prediction['predictions']) > 0:
        fig = go.Figure()
        
        # Current price
        fig.add_trace(go.Scatter(
            x=[0], y=[prediction['current_price']],
            mode='markers',
            marker=dict(size=15, color='blue'),
            name='Current Price'
        ))
        
        # Predictions
        fig.add_trace(go.Scatter(
            x=list(range(1, len(prediction['predictions']) + 1)),
            y=prediction['predictions'],
            mode='lines+markers',
            line=dict(color='green' if prediction['trend'] == 'bullish' else 'red'),
            name='Predictions'
        ))
        
        fig.update_layout(
            title=f"5-Day Price Prediction ({prediction['trend'].upper()})",
            xaxis_title="Days Ahead",
            yaxis_title="Price",
            height=400
        )
        
        st.plotly_chart(fig, use_container_width=True)

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
