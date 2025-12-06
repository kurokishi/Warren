import os
import sys
import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime, timedelta
import time
import warnings
warnings.filterwarnings('ignore')

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
    page_title="WarrenAI - Stock Analysis & Prediction",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS untuk tampilan yang lebih baik
st.markdown("""
<style>
    .main-title {
        font-size: 2.8rem;
        color: #1E3A8A;
        text-align: center;
        margin-bottom: 1rem;
        font-weight: 800;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
    }
    .sub-title {
        font-size: 1.2rem;
        color: #4B5563;
        text-align: center;
        margin-bottom: 2rem;
    }
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1.5rem;
        border-radius: 15px;
        color: white;
        margin-bottom: 1rem;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        transition: transform 0.3s ease;
    }
    .metric-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 8px 12px rgba(0, 0, 0, 0.15);
    }
    .prediction-card {
        background-color: #F8FAFC;
        padding: 1.2rem;
        border-radius: 12px;
        border: 2px solid #E2E8F0;
        margin: 0.5rem 0;
        transition: all 0.3s ease;
    }
    .prediction-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 12px rgba(0, 0, 0, 0.1);
        border-color: #3B82F6;
    }
    .success-box {
        background-color: #D1FAE5;
        padding: 1.2rem;
        border-radius: 12px;
        border-left: 6px solid #10B981;
    }
    .warning-box {
        background-color: #FEF3C7;
        padding: 1.2rem;
        border-radius: 12px;
        border-left: 6px solid #F59E0B;
    }
    .error-box {
        background-color: #FEE2E2;
        padding: 1.2rem;
        border-radius: 12px;
        border-left: 6px solid #EF4444;
    }
    .info-box {
        background-color: #DBEAFE;
        padding: 1.2rem;
        border-radius: 12px;
        border-left: 6px solid #3B82F6;
    }
    .stTabs [data-baseweb="tab-list"] {
        gap: 4px;
    }
    .stTabs [data-baseweb="tab"] {
        height: 55px;
        white-space: pre-wrap;
        background-color: #F1F5F9;
        border-radius: 8px 8px 0px 0px;
        padding: 15px 20px;
        font-weight: 600;
        font-size: 1rem;
        transition: all 0.3s ease;
    }
    .stTabs [data-baseweb="tab"]:hover {
        background-color: #E2E8F0;
    }
    .stTabs [aria-selected="true"] {
        background-color: #3B82F6 !important;
        color: white !important;
        box-shadow: 0 2px 4px rgba(59, 130, 246, 0.3);
    }
    .stock-badge {
        display: inline-block;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 6px 14px;
        border-radius: 20px;
        font-size: 0.9rem;
        font-weight: 600;
        margin: 2px;
        cursor: pointer;
        transition: all 0.3s ease;
    }
    .stock-badge:hover {
        transform: scale(1.05);
        box-shadow: 0 4px 8px rgba(102, 126, 234, 0.3);
    }
    .refresh-button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important;
        color: white !important;
        border: none !important;
        font-weight: 600 !important;
        padding: 12px 24px !important;
        border-radius: 10px !important;
        transition: all 0.3s ease !important;
    }
    .refresh-button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 12px rgba(102, 126, 234, 0.3) !important;
    }
    .trend-up {
        color: #10B981;
        font-weight: 700;
    }
    .trend-down {
        color: #EF4444;
        font-weight: 700;
    }
    .trend-neutral {
        color: #6B7280;
        font-weight: 700;
    }
    .footer {
        text-align: center;
        padding: 2rem;
        color: #6B7280;
        font-size: 0.9rem;
        margin-top: 3rem;
        border-top: 1px solid #E5E7EB;
    }
    .market-status-open {
        display: inline-block;
        background-color: #10B981;
        color: white;
        padding: 4px 12px;
        border-radius: 20px;
        font-size: 0.8rem;
        font-weight: 600;
    }
    .market-status-closed {
        display: inline-block;
        background-color: #EF4444;
        color: white;
        padding: 4px 12px;
        border-radius: 20px;
        font-size: 0.8rem;
        font-weight: 600;
    }
    .debug-info {
        font-family: monospace;
        background-color: #F3F4F6;
        padding: 10px;
        border-radius: 5px;
        font-size: 0.8rem;
        margin-top: 10px;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'last_ticker' not in st.session_state:
    st.session_state.last_ticker = None
if 'prediction_history' not in st.session_state:
    st.session_state.prediction_history = []
if 'predictor' not in st.session_state:
    st.session_state.predictor = None
if 'show_history' not in st.session_state:
    st.session_state.show_history = False
if 'auto_refresh' not in st.session_state:
    st.session_state.auto_refresh = False
if 'last_result' not in st.session_state:
    st.session_state.last_result = None

# Helper functions dengan safe access
def format_currency(value):
    """Format nilai menjadi currency Rupiah"""
    try:
        if value is None or value == 0:
            return "Rp 0"
        return f"Rp {float(value):,.2f}"
    except:
        return "Rp 0"

def format_percentage(value):
    """Format nilai menjadi persentase"""
    try:
        if value is None:
            return "0.00%"
        if float(value) >= 0:
            return f"+{float(value):.2f}%"
        return f"{float(value):.2f}%"
    except:
        return "0.00%"

def get_trend_color(trend):
    """Get color based on trend"""
    try:
        if not trend:
            return "#3B82F6"
        trend_lower = str(trend).lower()
        if 'bullish' in trend_lower:
            return "#10B981"
        elif 'bearish' in trend_lower:
            return "#EF4444"
        elif 'sideways' in trend_lower:
            return "#6B7280"
        else:
            return "#3B82F6"
    except:
        return "#3B82F6"

def safe_get(result, key, default):
    """Safe get from dictionary with debug info"""
    try:
        if key in result:
            return result[key]
        else:
            # Log missing key for debugging
            if st.session_state.get('debug_mode', False):
                st.warning(f"⚠️ Key '{key}' not found in result. Using default: {default}")
            return default
    except:
        return default

def create_price_chart(predictions, current_price, ticker):
    """Create interactive price prediction chart"""
    try:
        days = list(range(len(predictions) + 1))
        prices = [current_price] + predictions
        
        fig = go.Figure()
        
        # Add current price point
        fig.add_trace(go.Scatter(
            x=[0], 
            y=[current_price],
            mode='markers+text',
            name='Harga Saat Ini',
            marker=dict(
                size=15,
                color='#3B82F6',
                symbol='star',
                line=dict(width=2, color='white')
            ),
            text=[f"Rp {current_price:,.0f}"],
            textposition="top center"
        ))
        
        # Add prediction line
        fig.add_trace(go.Scatter(
            x=days, 
            y=prices,
            mode='lines+markers+text',
            name='Prediksi',
            line=dict(color='#10B981', width=4),
            marker=dict(size=10, color='#10B981'),
            text=[f"Rp {p:,.0f}" for p in prices],
            textposition="top center"
        ))
        
        # Add confidence interval (shaded area)
        if len(predictions) > 0:
            volatility = np.std(predictions) / current_price if current_price > 0 else 0.02
            upper_bound = [current_price * (1 + volatility * i * 0.8) for i in range(len(prices))]
            lower_bound = [current_price * (1 - volatility * i * 0.8) for i in range(len(prices))]
            
            fig.add_trace(go.Scatter(
                x=days + days[::-1],
                y=upper_bound + lower_bound[::-1],
                fill='toself',
                fillcolor='rgba(59, 130, 246, 0.15)',
                line=dict(color='rgba(255,255,255,0)'),
                name='Confidence Interval (80%)',
                showlegend=True,
                hoverinfo='skip'
            ))
        
        # Update layout
        fig.update_layout(
            title=f"📈 Prediksi Harga {ticker}",
            xaxis_title="Hari",
            yaxis_title="Harga (Rp)",
            hovermode="x unified",
            template="plotly_white",
            height=500,
            showlegend=True,
            legend=dict(
                yanchor="top",
                y=0.99,
                xanchor="left",
                x=0.01,
                bgcolor='rgba(255, 255, 255, 0.9)',
                bordercolor='#E5E7EB',
                borderwidth=1
            ),
            plot_bgcolor='rgba(240, 240, 240, 0.5)',
            paper_bgcolor='rgba(255, 255, 255, 0.1)',
            margin=dict(l=50, r=50, t=80, b=50)
        )
        
        # Add grid and formatting
        fig.update_xaxes(
            showgrid=True, 
            gridwidth=1, 
            gridcolor='lightgray',
            tickmode='array',
            tickvals=days,
            ticktext=[f'Hari {i}' if i == 0 else f'H+{i}' for i in days]
        )
        fig.update_yaxes(
            showgrid=True, 
            gridwidth=1, 
            gridcolor='lightgray',
            tickformat=',.0f'
        )
        
        return fig
    except Exception as e:
        st.error(f"Error creating chart: {e}")
        return None

def display_prediction_results(result, ticker):
    """Display prediction results in a nice format dengan safe access"""
    
    # Cek jika ada error
    if safe_get(result, 'error', False):
        error_msg = safe_get(result, 'message', 'Unknown error')
        st.error(f"❌ {error_msg}")
        return
    
    # Safe extraction dengan default values
    current_price = safe_get(result, 'current_price', 0)
    trend = safe_get(result, 'trend', 'unknown')
    trend_icon = safe_get(result, 'trend_icon', '📊')
    trend_percentage = safe_get(result, 'trend_percentage', 0.0)
    confidence = safe_get(result, 'confidence', 50.0)
    volatility_pct = safe_get(result, 'volatility_pct', 1.5)
    potential_change_pct = safe_get(result, 'potential_change_pct', 0.0)
    predictions = safe_get(result, 'predictions', [])
    next_day_prediction = safe_get(result, 'next_day_prediction', current_price)
    avg_prediction = safe_get(result, 'avg_prediction', current_price)
    
    # Ensure predictions is a list
    if not isinstance(predictions, list):
        predictions = []
    
    # Ensure we have at least some predictions
    if len(predictions) == 0 and current_price > 0:
        predictions = [current_price] * 5
        next_day_prediction = current_price
        avg_prediction = current_price
    
    # Header dengan ticker dan timestamp
    col1, col2, col3 = st.columns([3, 1, 1])
    with col1:
        st.markdown(f"### 📊 Analisis Teknis & Prediksi: **{ticker}**")
    with col2:
        st.caption(f"Data: {safe_get(result, 'latest_data_date', 'N/A')}")
    with col3:
        st.caption(f"Update: {datetime.now().strftime('%H:%M:%S')}")
    
    # Key metrics dalam 4 kolom
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        st.markdown("##### 💰 HARGA SAAT INI")
        st.markdown(f"# {format_currency(current_price)}")
        change_pct = potential_change_pct
        trend_color = "#10B981" if change_pct >= 0 else "#EF4444"
        st.markdown(f'<p style="color: {trend_color}; font-size: 1.2rem;">{format_percentage(change_pct)} (besok)</p>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col2:
        trend_color = get_trend_color(trend)
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        st.markdown(f"##### {trend_icon} TREND PREDIKSI")
        st.markdown(f"# {trend.upper()}")
        st.markdown(f'<p style="color: {trend_color}; font-size: 1.2rem;">{format_percentage(trend_percentage)}</p>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col3:
        if confidence > 70:
            color = "#10B981"
            label = "TINGGI"
        elif confidence > 50:
            color = "#F59E0B"
            label = "SEDANG"
        else:
            color = "#EF4444"
            label = "RENDAH"
        
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        st.markdown("##### 🎯 CONFIDENCE LEVEL")
        st.markdown(f"# {confidence:.1f}%")
        st.markdown(f'<p style="color: {color}; font-size: 1rem;">{label}</p>', unsafe_allow_html=True)
        
        # Progress bar
        progress_html = f"""
        <div style="background: #E5E7EB; border-radius: 10px; height: 10px; margin-top: 10px;">
            <div style="background: {color}; width: {min(confidence, 100)}%; height: 100%; border-radius: 10px;"></div>
        </div>
        """
        st.markdown(progress_html, unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col4:
        if volatility_pct > 3:
            color = "#EF4444"
            label = "TINGGI"
        elif volatility_pct > 1.5:
            color = "#F59E0B"
            label = "SEDANG"
        else:
            color = "#10B981"
            label = "RENDAH"
        
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        st.markdown("##### 📊 VOLATILITAS")
        st.markdown(f"# {volatility_pct:.1f}%")
        st.markdown(f'<p style="color: {color}; font-size: 1rem;">{label}</p>', unsafe_allow_html=True)
        st.markdown(f'<small>Volatilitas harian historis</small>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Divider
    st.markdown("---")
    
    # Tabs untuk berbagai tampilan
    tab1, tab2, tab3, tab4 = st.tabs([
        "📅 PREDIKSI HARIAN", 
        "📈 GRAFIK INTERAKTIF", 
        "🎯 ANALISIS TEKNIS",
        "📋 INFORMASI DETAIL"
    ])
    
    with tab1:
        # Daily predictions table dengan styling
        st.subheader("Prediksi Harga per Hari")
        
        if len(predictions) > 0:
            pred_data = []
            for i, price in enumerate(predictions):
                if i == 0:
                    change_pct = potential_change_pct
                else:
                    change_pct = ((price - current_price) / current_price * 100)
                
                vs_yesterday = ((price - predictions[i-1]) / predictions[i-1] * 100) if i > 0 else 0
                
                pred_data.append({
                    'HARI': f'H+{i+1}',
                    'TANGGAL': (datetime.now() + timedelta(days=i+1)).strftime('%d %b'),
                    'PREDIKSI HARGA': price,
                    'PERUBAHAN': change_pct,
                    'VS KEMARIN': vs_yesterday
                })
            
            # Display dengan formatting
            for idx, row in enumerate(pred_data):
                with st.container():
                    col1, col2, col3, col4 = st.columns([1, 2, 2, 2])
                    
                    with col1:
                        st.markdown(f"**{row['HARI']}**")
                        st.caption(row['TANGGAL'])
                    
                    with col2:
                        st.markdown(f"**{format_currency(row['PREDIKSI HARGA'])}**")
                    
                    with col3:
                        color = "#10B981" if row['PERUBAHAN'] >= 0 else "#EF4444"
                        st.markdown(f'<span style="color: {color}; font-weight: bold;">{format_percentage(row["PERUBAHAN"])}</span>', unsafe_allow_html=True)
                    
                    with col4:
                        if idx > 0:
                            color = "#10B981" if row['VS KEMARIN'] >= 0 else "#EF4444"
                            st.markdown(f'<span style="color: {color}; font-weight: bold;">{format_percentage(row["VS KEMARIN"])}</span>', unsafe_allow_html=True)
                    
                    if idx < len(pred_data) - 1:
                        st.divider()
        else:
            st.info("Tidak ada prediksi yang tersedia")
        
        # Summary metrics
        st.subheader("📊 Ringkasan Prediksi")
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric(
                label="Prediksi Besok",
                value=format_currency(next_day_prediction),
                delta=format_percentage(potential_change_pct)
            )
        
        with col2:
            st.metric(
                label="Rata-rata Prediksi",
                value=format_currency(avg_prediction),
                delta=format_percentage(trend_percentage)
            )
        
        with col3:
            if len(predictions) > 0:
                best_day_idx = np.argmax(predictions)
                best_day_price = predictions[best_day_idx]
                best_day_change = ((best_day_price - current_price) / current_price * 100)
                st.metric(
                    label=f"Hari Terbaik (H+{best_day_idx + 1})",
                    value=format_currency(best_day_price),
                    delta=format_percentage(best_day_change)
                )
            else:
                st.metric(
                    label="Hari Terbaik",
                    value=format_currency(current_price),
                    delta="0.00%"
                )
        
        with col4:
            if len(predictions) > 0:
                total_change = ((predictions[-1] - current_price) / current_price * 100)
                st.metric(
                    label="Perubahan Total",
                    value=format_percentage(total_change),
                    delta="selama periode"
                )
            else:
                st.metric(
                    label="Perubahan Total",
                    value="0.00%",
                    delta="selama periode"
                )
    
    with tab2:
        # Interactive chart
        st.subheader("📈 Visualisasi Prediksi")
        
        if current_price > 0 and len(predictions) > 0:
            fig = create_price_chart(predictions, current_price, ticker)
            if fig:
                st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("Data tidak cukup untuk membuat grafik")
        
        # Range realistis
        st.subheader("🎯 Range Realistis")
        
        realistic_range = safe_get(result, 'realistic_range', {
            'optimistic': current_price * 1.05,
            'pessimistic': current_price * 0.95,
            'most_likely': current_price
        })
        
        col1, col2, col3 = st.columns(3)
        
        range_data = [
            ("Optimistis", realistic_range.get('optimistic', current_price * 1.05), "#10B981", "➕"),
            ("Paling Mungkin", realistic_range.get('most_likely', current_price), "#3B82F6", "🎯"),
            ("Pesimistis", realistic_range.get('pessimistic', current_price * 0.95), "#EF4444", "➖")
        ]
        
        for name, value, color, icon in range_data:
            with col1 if name == "Optimistis" else col2 if name == "Paling Mungkin" else col3:
                st.markdown(f'<div style="background-color: {color}20; padding: 20px; border-radius: 15px; border-left: 5px solid {color}">', unsafe_allow_html=True)
                st.markdown(f"##### {icon} {name}")
                st.markdown(f"**{format_currency(value)}**")
                change_pct = ((value - current_price) / current_price * 100)
                st.markdown(f'<span style="color: {color}; font-weight: bold;">{format_percentage(change_pct)}</span>', unsafe_allow_html=True)
                st.markdown('</div>', unsafe_allow_html=True)
    
    with tab3:
        # Technical analysis
        st.subheader("🎯 Analisis Teknis Mendalam")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("##### 📊 Bollinger Bands")
            bb = safe_get(result, 'bollinger_bands', None)
            if bb:
                # Display bands info
                st.markdown("**Detail Bollinger Bands:**")
                
                bands_info = [
                    ("Upper Band", bb.get('upper', 0), "#EF4444"),
                    ("Middle Band (MA20)", bb.get('middle', 0), "#3B82F6"),
                    ("Lower Band", bb.get('lower', 0), "#10B981")
                ]
                
                for name, value, color in bands_info:
                    col_a, col_b = st.columns([2, 1])
                    with col_a:
                        st.markdown(f"**{name}**")
                    with col_b:
                        st.markdown(f'<span style="color: {color}; font-weight: bold;">{format_currency(value)}</span>', unsafe_allow_html=True)
                
                if 'width_pct' in bb:
                    st.markdown(f"**Band Width:** {bb['width_pct']:.1f}%")
                
                # Interpretation
                upper = bb.get('upper', 0)
                lower = bb.get('lower', 0)
                if upper > lower:
                    position = ((current_price - lower) / (upper - lower)) * 100
                    
                    if position > 80:
                        st.markdown('<div class="warning-box">', unsafe_allow_html=True)
                        st.markdown("**⚠️ OVERBOUGHT**")
                        st.markdown("Harga mendekati resistance, potensi koreksi")
                        st.markdown('</div>', unsafe_allow_html=True)
                    elif position < 20:
                        st.markdown('<div class="info-box">', unsafe_allow_html=True)
                        st.markdown("**ℹ️ OVERSOLD**")
                        st.markdown("Harga mendekati support, potensi rebound")
                        st.markdown('</div>', unsafe_allow_html=True)
                    else:
                        st.markdown('<div class="success-box">', unsafe_allow_html=True)
                        st.markdown("**✅ NORMAL RANGE**")
                        st.markdown("Harga dalam range normal Bollinger Bands")
                        st.markdown('</div>', unsafe_allow_html=True)
                else:
                    st.info("Data Bollinger Bands tidak cukup")
            else:
                st.info("Bollinger Bands tidak tersedia untuk analisis ini")
        
        with col2:
            st.markdown("##### 🎯 Support & Resistance")
            sr = safe_get(result, 'support_resistance', {})
            
            if sr:
                # Current price vs S/R
                st.markdown("**Level Penting:**")
                
                levels = []
                if 'recent_high' in sr:
                    levels.append(('🔼 Resistance', sr['recent_high']))
                if 'recent_low' in sr:
                    levels.append(('🔽 Support', sr['recent_low']))
                
                for name, value in levels:
                    diff_pct = ((value - current_price) / current_price * 100)
                    color = "#EF4444" if 'Resistance' in name else "#10B981"
                    
                    col_a, col_b, col_c = st.columns([2, 2, 1])
                    with col_a:
                        st.markdown(f"**{name}**")
                    with col_b:
                        st.markdown(f"**{format_currency(value)}**")
                    with col_c:
                        st.markdown(f'<span style="color: {color}; font-weight: bold;">{format_percentage(diff_pct)}</span>', unsafe_allow_html=True)
                
                # Psychological levels
                if 'psychological_levels' in sr and sr['psychological_levels']:
                    st.markdown("**🎯 Level Psikologis:**")
                    for level in sr['psychological_levels']:
                        diff_pct = ((level - current_price) / current_price * 100)
                        st.markdown(f"- {format_currency(level)} ({format_percentage(diff_pct)})")
            else:
                st.info("Support & Resistance tidak tersedia untuk analisis ini")
    
    with tab4:
        # Information tab
        st.subheader("📋 Informasi Detail")
        
        # Data grid
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("##### 🔧 Parameter Prediksi")
            info_data = {
                'Ticker': safe_get(result, 'ticker', ticker),
                'Sumber Data Harga': safe_get(result, 'price_source', 'N/A'),
                'Jumlah Data Historis': f"{safe_get(result, 'data_points', 0)} points",
                'Tanggal Data Terakhir': safe_get(result, 'latest_data_date', 'N/A'),
                'Prediction Days': len(predictions),
                'Max Daily Change': "±3%",
                'Confidence Algorithm': "Conservative Mean Reversion"
            }
            
            for key, value in info_data.items():
                st.markdown(f"**{key}:** {value}")
        
        with col2:
            st.markdown("##### ⚙️ System Info")
            sys_data = {
                'Waktu Pemrosesan': f"{safe_get(result, 'processing_time', 0)} detik",
                'Cache Digunakan': "✅ Ya" if safe_get(result, 'cache_used', False) else "❌ Tidak",
                'Harga Real-time': "✅ Digunakan" if safe_get(result, 'realtime_price_used', False) else "❌ Tidak tersedia",
                'Model yang Digunakan': "Volatility Random Walk",
                'Mean Reversion Factor': "30%"
            }
            
            for key, value in sys_data.items():
                st.markdown(f"**{key}:** {value}")
        
        # Performance metrics
        st.markdown("##### 📊 Performance Metrics")
        perf_cols = st.columns(4)
        
        with perf_cols[0]:
            st.metric("Volatility", f"{volatility_pct:.1f}%")
        with perf_cols[1]:
            st.metric("Confidence", f"{confidence:.1f}%")
        with perf_cols[2]:
            st.metric("Trend Strength", f"{abs(trend_percentage):.1f}%")
        with perf_cols[3]:
            cache_status = "HIT" if safe_get(result, 'cache_used', False) else "MISS"
            st.metric("Cache Status", cache_status)
        
        # Disclaimer
        st.markdown("---")
        st.markdown("##### ⚠️ PERINGATAN & DISCLAIMER")
        
        disclaimer_text = safe_get(result, 'disclaimer', 
            "Prediksi didasarkan pada volatilitas historis. Pergerakan aktual bisa berbeda. Gunakan hanya sebagai referensi tambahan.")
        
        st.markdown(f"""
        <div class="warning-box">
        <h5>📢 INFORMASI PENTING</h5>
        
        1. **BUKAN REKOMENDASI INVESTASI** - Prediksi ini bersifat informatif dan edukatif<br>
        2. **AKURASI TIDAK DIJAMIN** - Prediksi didasarkan pada model probabilistik<br>
        3. **RISIKO INVESTASI** - Saham mengandung risiko, nilai dapat naik atau turun<br>
        4. **LITERASI KEUANGAN** - Pastikan Anda memahami produk investasi<br>
        5. **DIVERSIFIKASI** - Jangan menaruh semua modal dalam satu saham<br>
        6. **KONSULTASI PROFESIONAL** - Konsultasikan dengan penasihat keuangan<br>
        7. **PAST PERFORMANCE** - Tidak menjamin future performance<br>
        
        <strong>Investasi yang bijak adalah investasi yang terinformasi dengan baik!</strong>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown(f"<small>{disclaimer_text}</small>", unsafe_allow_html=True)

def price_prediction_panel():
    """Panel utama untuk prediksi harga"""
    st.markdown('<h1 class="main-title">📈 WARRENAI STOCK PREDICTOR</h1>', unsafe_allow_html=True)
    st.markdown('<p class="sub-title">Prediksi harga saham berbasis AI dengan pendekatan konservatif untuk pasar Indonesia</p>', unsafe_allow_html=True)
    
    # Sidebar untuk input
    with st.sidebar:
        st.markdown("### ⚙️ PARAMETER INPUT")
        st.markdown("---")
        
        # Ticker input dengan search
        ticker = st.text_input(
            "**MASUKKAN TICKER SAHAM:**",
            value="TLKM.JK",
            placeholder="TLKM.JK, BBCA.JK, BBRI.JK",
            help="Format: KODE.JK (contoh: TLKM.JK)"
        ).strip().upper()
        
        # Auto-format ticker
        if ticker and not ticker.endswith('.JK'):
            ticker = f"{ticker}.JK"
        
        # Market status
        current_hour = datetime.now().hour
        market_open = 9 <= current_hour < 16
        market_status = "🟢 BURSA BUKA" if market_open else "🔴 BURSA TUTUP"
        
        st.markdown(f"**Status Pasar:** {market_status}")
        st.markdown(f"**Waktu:** {datetime.now().strftime('%H:%M:%S')}")
        
        st.markdown("---")
        
        # Quick ticker selection
        st.markdown("**🚀 TICKER CEPAT:**")
        
        # Blue chip stocks
        blue_chips = {
            "BBCA": "BBCA.JK",
            "BBRI": "BBRI.JK", 
            "BMRI": "BMRI.JK",
            "TLKM": "TLKM.JK",
            "ASII": "ASII.JK",
            "UNVR": "UNVR.JK"
        }
        
        cols = st.columns(3)
        for idx, (name, code) in enumerate(blue_chips.items()):
            with cols[idx % 3]:
                if st.button(f"📈 {name}", use_container_width=True, key=f"btn_{name}"):
                    ticker = code
                    st.session_state.last_ticker = None  # Force refresh
                    st.rerun()
        
        # Prediction parameters
        st.markdown("---")
        st.markdown("**🔮 SETTING PREDIKSI:**")
        
        prediction_days = st.slider(
            "Jumlah Hari Prediksi:",
            min_value=1,
            max_value=10,
            value=5,
            help="Prediksi harga untuk N hari ke depan"
        )
        
        # Advanced options
        with st.expander("⚡ ADVANCED OPTIONS"):
            use_cache = st.checkbox("Gunakan Cache", value=True, 
                                   help="Cache data untuk performa lebih cepat")
            
            auto_refresh = st.checkbox("Auto Refresh (60s)", value=False,
                                      help="Refresh data otomatis setiap 60 detik")
            
            st.session_state.auto_refresh = auto_refresh
            
            debug_mode = st.checkbox("Debug Mode", value=False,
                                    help="Tampilkan informasi debug")
            
            st.session_state.debug_mode = debug_mode
        
        # Action buttons
        st.markdown("---")
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("🔄 CLEAR CACHE", use_container_width=True, type="secondary"):
                if st.session_state.predictor:
                    st.session_state.predictor.clear_cache()
                st.session_state.last_ticker = None
                st.success("Cache cleared!")
                time.sleep(1)
                st.rerun()
        
        with col2:
            if st.button("📊 VIEW HISTORY", use_container_width=True, type="secondary"):
                st.session_state.show_history = not st.session_state.get('show_history', False)
                st.rerun()
    
    # Main content area
    if not ticker or ticker == ".JK":
        st.warning("⚠️ Silakan masukkan ticker saham di sidebar")
        st.info("💡 Contoh ticker: TLKM.JK, BBCA.JK, BBRI.JK")
        return
    
    # Initialize predictor jika belum ada
    if st.session_state.predictor is None:
        try:
            from ai.price_predictor import ConservativePricePredictor
            st.session_state.predictor = ConservativePricePredictor()
            if st.session_state.debug_mode:
                st.success("✅ Predictor initialized successfully!")
        except Exception as e:
            st.error(f"❌ Gagal menginisialisasi predictor: {str(e)}")
            with st.expander("Debug Information"):
                st.write(f"Error: {str(e)}")
                st.write(f"ROOT: {ROOT}")
                st.write(f"Current dir: {os.getcwd()}")
                st.write("Files in current directory:")
                for f in os.listdir('.'):
                    st.write(f"  - {f}")
            return
    
    # Check if ticker changed
    if ticker != st.session_state.last_ticker:
        st.session_state.last_ticker = ticker
        if st.session_state.predictor:
            st.session_state.predictor.clear_cache(ticker)
        
        # Show loading message
        with st.spinner(f"🔄 Memuat data baru untuk {ticker}..."):
            time.sleep(0.5)  # Small delay for visual feedback
    
    # Auto-refresh logic
    if st.session_state.auto_refresh:
        st.info("🔄 Auto refresh aktif - data akan di-refresh setiap 60 detik")
        time.sleep(60)
        st.rerun()
    
    # Prediction button
    st.markdown("---")
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        predict_button = st.button(
            "🚀 LAKUKAN PREDIKSI", 
            type="primary", 
            use_container_width=True,
            key="predict_button"
        )
    
    # Store last result for debugging
    last_result = st.session_state.get('last_result')
    
    # Perform prediction when button clicked
    if predict_button or st.session_state.auto_refresh:
        with st.spinner(f"🔍 Menganalisis {ticker}..."):
            try:
                # Get prediction using the new method
                result = st.session_state.predictor.predict_for_ticker(
                    ticker=ticker,
                    days=prediction_days,
                    use_cache=use_cache
                )
                
                # Store result for debugging
                st.session_state.last_result = result
                
                # Store in history
                history_entry = {
                    'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    'ticker': ticker,
                    'result': result.copy()
                }
                st.session_state.prediction_history.insert(0, history_entry)
                
                # Limit history size
                if len(st.session_state.prediction_history) > 20:
                    st.session_state.prediction_history.pop()
                
                # Display results
                display_prediction_results(result, ticker)
                
                # Debug information if enabled
                if st.session_state.debug_mode and not result.get('error'):
                    with st.expander("🔧 Debug Result Structure"):
                        st.write("Result keys:", list(result.keys()))
                        st.write("Result values:")
                        for key, value in result.items():
                            st.write(f"  - {key}: {value}")
                
            except Exception as e:
                st.error(f"❌ Error dalam prediksi: {str(e)}")
                
                # Debug information
                with st.expander("🔧 Debug Information"):
                    st.write("**Error details:**", str(e))
                    st.write("**Ticker:**", ticker)
                    st.write("**Predictor type:**", type(st.session_state.predictor))
                    
                    # Check if predictor has the method
                    if hasattr(st.session_state.predictor, 'predict_for_ticker'):
                        st.success("✅ Method predict_for_ticker exists!")
                    else:
                        st.error("❌ Method predict_for_ticker NOT FOUND!")
                        available_methods = [m for m in dir(st.session_state.predictor) 
                                           if not m.startswith('_')]
                        st.write("Available methods:", available_methods)
                    
                    # Show last result if available
                    if last_result:
                        st.write("**Last result structure:**")
                        st.write(last_result)
    
    # Show last result if available and no button clicked yet
    elif last_result and not st.session_state.auto_refresh:
        display_prediction_results(last_result, ticker)
    
    # Show prediction history if requested
    if st.session_state.get('show_history', False) and st.session_state.prediction_history:
        st.markdown("---")
        st.markdown("### 📜 RIWAYAT PREDIKSI")
        
        for i, entry in enumerate(st.session_state.prediction_history[:10]):
            with st.container():
                col1, col2, col3, col4 = st.columns([2, 2, 2, 2])
                
                with col1:
                    st.markdown(f"**{entry['ticker']}**")
                
                with col2:
                    st.markdown(f"`{entry['timestamp']}`")
                
                with col3:
                    if not entry['result'].get('error'):
                        trend = entry['result'].get('trend', 'N/A')
                        icon = entry['result'].get('trend_icon', '📊')
                        st.markdown(f"{icon} **{trend}**")
                
                with col4:
                    if not entry['result'].get('error'):
                        price = entry['result'].get('current_price', 0)
                        st.markdown(f"**{format_currency(price)}**")
                
                if i < len(st.session_state.prediction_history[:10]) - 1:
                    st.divider()
        
        if st.button("Tutup Riwayat", type="secondary"):
            st.session_state.show_history = False
            st.rerun()
    
    # Footer
    st.markdown("---")
    st.markdown("""
    <div class="footer">
    <p>📈 <strong>WarrenAI Stock Predictor</strong> - v1.0.0</p>
    <p>Dikembangkan dengan ❤️ untuk investor Indonesia</p>
    <p>⚠️ Gunakan dengan bijak. Investasi mengandung risiko.</p>
    </div>
    """, unsafe_allow_html=True)

def main():
    try:
        # Main navigation
        st.sidebar.markdown("## 🧭 NAVIGASI")
        
        # App mode selection
        app_mode = st.sidebar.radio(
            "Pilih Mode Aplikasi:",
            ["📈 Price Prediction", "📊 Stock Screener", "📋 Portfolio", "⚙️ Settings"],
            index=0,
            label_visibility="collapsed"
        )
        
        st.sidebar.markdown("---")
        st.sidebar.markdown("### ℹ️ Tentang")
        st.sidebar.info("""
        **WarrenAI Stock Predictor**
        
        Aplikasi prediksi harga saham berbasis AI dengan pendekatan konservatif untuk pasar Indonesia.
        
        **Fitur:**
        - Prediksi harga 1-10 hari ke depan
        - Analisis teknis lengkap
        - Real-time data dari Yahoo Finance
        - Trading scenarios
        
        **Version:** 1.0.0
        """)
        
        # Run selected mode
        if app_mode == "📈 Price Prediction":
            price_prediction_panel()
        elif app_mode == "📊 Stock Screener":
            try:
                from ui.screener_panel import screener_panel
                screener_panel()
            except:
                st.title("📊 Stock Screener")
                st.info("Fitur Stock Screener akan segera hadir!")
        elif app_mode == "📋 Portfolio":
            try:
                from ui.portfolio_panel import portfolio_panel
                portfolio_panel()
            except:
                st.title("📋 Portfolio Management")
                st.info("Fitur Portfolio Management akan segera hadir!")
        else:  # Settings
            st.title("⚙️ Settings")
            st.info("Pengaturan aplikasi akan segera hadir!")
            
    except Exception as e:
        st.error(f"❌ Application Error: {str(e)}")
        
        # Debug information
        with st.expander("🐛 Debug Information"):
            st.write("**Error details:**", str(e))
            st.write("**Current directory:**", os.getcwd())
            st.write("**Python path:**", sys.path[:5])
            
            # Check for ai module
            ai_path = os.path.join(ROOT, 'ai')
            if os.path.exists(ai_path):
                st.success(f"✅ AI folder exists: {ai_path}")
                st.write("**Files in ai folder:**")
                for item in os.listdir(ai_path):
                    st.write(f"  - {item}")
            else:
                st.error(f"❌ AI folder not found: {ai_path}")
            
            # Check for price_predictor.py
            predictor_path = os.path.join(ai_path, 'price_predictor.py')
            if os.path.exists(predictor_path):
                st.success(f"✅ price_predictor.py exists: {predictor_path}")
            else:
                st.error(f"❌ price_predictor.py not found: {predictor_path}")

if __name__ == "__main__":
    main()
