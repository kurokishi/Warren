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

# Helper functions
def format_currency(value):
    """Format nilai menjadi currency Rupiah"""
    if value == 0:
        return "Rp 0"
    return f"Rp {value:,.2f}"

def format_percentage(value):
    """Format nilai menjadi persentase"""
    if value >= 0:
        return f"+{value:.2f}%"
    return f"{value:.2f}%"

def get_trend_color(trend):
    """Get color based on trend"""
    trend_lower = trend.lower()
    if 'bullish' in trend_lower:
        return "#10B981"
    elif 'bearish' in trend_lower:
        return "#EF4444"
    elif 'sideways' in trend_lower:
        return "#6B7280"
    else:
        return "#3B82F6"

def create_price_chart(predictions, current_price, ticker):
    """Create interactive price prediction chart"""
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

def create_technical_analysis_chart(result):
    """Create technical analysis chart with Bollinger Bands"""
    if not result.get('bollinger_bands'):
        return None
    
    bb = result['bollinger_bands']
    current_price = result['current_price']
    
    fig = go.Figure()
    
    # Add Bollinger Bands
    bands_data = [
        ('Upper Band', bb['upper'], '#EF4444'),
        ('Middle Band (MA20)', bb['middle'], '#3B82F6'),
        ('Lower Band', bb['lower'], '#10B981')
    ]
    
    for name, value, color in bands_data:
        fig.add_trace(go.Indicator(
            mode="number",
            value=value,
            number={'prefix': "Rp ", 'valueformat': ",.0f"},
            title={'text': name, 'font': {'size': 14}},
            domain={'row': 0, 'column': len(bands_data)},
        ))
    
    # Add current price indicator
    fig.add_trace(go.Indicator(
        mode="number+delta",
        value=current_price,
        number={'prefix': "Rp ", 'valueformat': ",.0f"},
        delta={'reference': bb['middle'], 'relative': True, 'valueformat': '.1%'},
        title={'text': "Current Price", 'font': {'size': 16, 'color': get_trend_color(result['trend'])}},
        domain={'row': 1, 'column': 1}
    ))
    
    fig.update_layout(
        grid={'rows': 2, 'columns': 3, 'pattern': "independent"},
        height=300,
        paper_bgcolor='rgba(0,0,0,0)',
        margin=dict(l=20, r=20, t=30, b=20)
    )
    
    return fig

def display_prediction_results(result, ticker):
    """Display prediction results in a nice format"""
    
    if result.get('error'):
        st.error(f"❌ {result['message']}")
        return
    
    # Header dengan ticker dan timestamp
    col1, col2, col3 = st.columns([3, 1, 1])
    with col1:
        st.markdown(f"### 📊 Analisis Teknis & Prediksi: **{ticker}**")
    with col2:
        st.caption(f"Data: {result.get('latest_data_date', 'N/A')}")
    with col3:
        st.caption(f"Update: {datetime.now().strftime('%H:%M:%S')}")
    
    # Key metrics dalam 4 kolom
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        st.markdown("##### 💰 HARGA SAAT INI")
        st.markdown(f"# {format_currency(result['current_price'])}")
        change_pct = result['potential_change_pct']
        trend_color = "#10B981" if change_pct >= 0 else "#EF4444"
        st.markdown(f'<p style="color: {trend_color}; font-size: 1.2rem;">{format_percentage(change_pct)} (besok)</p>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col2:
        trend_color = get_trend_color(result['trend'])
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        st.markdown(f"##### {result['trend_icon']} TREND PREDIKSI")
        st.markdown(f"# {result['trend'].upper()}")
        st.markdown(f'<p style="color: {trend_color}; font-size: 1.2rem;">{format_percentage(result["trend_percentage"])}</p>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col3:
        confidence = result['confidence']
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
        st.markdown(f"# {confidence}%")
        st.markdown(f'<p style="color: {color}; font-size: 1rem;">{label}</p>', unsafe_allow_html=True)
        
        # Progress bar
        progress_html = f"""
        <div style="background: #E5E7EB; border-radius: 10px; height: 10px; margin-top: 10px;">
            <div style="background: {color}; width: {confidence}%; height: 100%; border-radius: 10px;"></div>
        </div>
        """
        st.markdown(progress_html, unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col4:
        volatility = result['volatility_pct']
        if volatility > 3:
            color = "#EF4444"
            label = "TINGGI"
        elif volatility > 1.5:
            color = "#F59E0B"
            label = "SEDANG"
        else:
            color = "#10B981"
            label = "RENDAH"
        
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        st.markdown("##### 📊 VOLATILITAS")
        st.markdown(f"# {volatility}%")
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
        
        pred_data = []
        for i, price in enumerate(result['predictions']):
            if i == 0:
                change_pct = result['potential_change_pct']
            else:
                change_pct = ((price - result['current_price']) / result['current_price'] * 100)
            
            vs_yesterday = ((price - result['predictions'][i-1]) / result['predictions'][i-1] * 100) if i > 0 else 0
            
            pred_data.append({
                'HARI': f'H+{i+1}',
                'TANGGAL': (datetime.now() + timedelta(days=i+1)).strftime('%d %b'),
                'PREDIKSI HARGA': price,
                'PERUBAHAN': change_pct,
                'VS KEMARIN': vs_yesterday
            })
        
        df_pred = pd.DataFrame(pred_data)
        
        # Display dengan formatting
        for idx, row in df_pred.iterrows():
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
                
                if idx < len(df_pred) - 1:
                    st.divider()
        
        # Summary metrics
        st.subheader("📊 Ringkasan Prediksi")
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric(
                label="Prediksi Besok",
                value=format_currency(result['next_day_prediction']),
                delta=format_percentage(result['potential_change_pct'])
            )
        
        with col2:
            st.metric(
                label="Rata-rata Prediksi",
                value=format_currency(result['avg_prediction']),
                delta=format_percentage(result['trend_percentage'])
            )
        
        with col3:
            # Hitung best day
            best_day_idx = np.argmax(result['predictions'])
            best_day_price = result['predictions'][best_day_idx]
            best_day_change = ((best_day_price - result['current_price']) / result['current_price'] * 100)
            st.metric(
                label=f"Hari Terbaik (H+{best_day_idx + 1})",
                value=format_currency(best_day_price),
                delta=format_percentage(best_day_change)
            )
        
        with col4:
            total_change = ((result['predictions'][-1] - result['current_price']) / result['current_price'] * 100)
            st.metric(
                label="Perubahan Total",
                value=format_percentage(total_change),
                delta="selama periode"
            )
    
    with tab2:
        # Interactive chart
        st.subheader("📈 Visualisasi Prediksi")
        
        fig = create_price_chart(result['predictions'], result['current_price'], ticker)
        st.plotly_chart(fig, use_container_width=True)
        
        # Range realistis
        st.subheader("🎯 Range Realistis")
        
        col1, col2, col3 = st.columns(3)
        
        range_data = [
            ("Optimistis", result['realistic_range']['optimistic'], "#10B981", "➕"),
            ("Paling Mungkin", result['realistic_range']['most_likely'], "#3B82F6", "🎯"),
            ("Pesimistis", result['realistic_range']['pessimistic'], "#EF4444", "➖")
        ]
        
        for name, value, color, icon in range_data:
            with col1 if name == "Optimistis" else col2 if name == "Paling Mungkin" else col3:
                st.markdown(f'<div style="background-color: {color}20; padding: 20px; border-radius: 15px; border-left: 5px solid {color}">', unsafe_allow_html=True)
                st.markdown(f"##### {icon} {name}")
                st.markdown(f"**{format_currency(value)}**")
                change_pct = ((value - result['current_price']) / result['current_price'] * 100)
                st.markdown(f'<span style="color: {color}; font-weight: bold;">{format_percentage(change_pct)}</span>', unsafe_allow_html=True)
                st.markdown('</div>', unsafe_allow_html=True)
    
    with tab3:
        # Technical analysis
        st.subheader("🎯 Analisis Teknis Mendalam")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("##### 📊 Bollinger Bands")
            if result.get('bollinger_bands'):
                bb = result['bollinger_bands']
                
                # Display bands info
                st.markdown("**Detail Bollinger Bands:**")
                
                bands_info = [
                    ("Upper Band", bb['upper'], "#EF4444"),
                    ("Middle Band (MA20)", bb['middle'], "#3B82F6"),
                    ("Lower Band", bb['lower'], "#10B981")
                ]
                
                for name, value, color in bands_info:
                    col_a, col_b = st.columns([2, 1])
                    with col_a:
                        st.markdown(f"**{name}**")
                    with col_b:
                        st.markdown(f'<span style="color: {color}; font-weight: bold;">{format_currency(value)}</span>', unsafe_allow_html=True)
                
                st.markdown(f"**Band Width:** {bb['width_pct']:.1f}%")
                
                # Interpretation
                current_price = result['current_price']
                position = ((current_price - bb['lower']) / (bb['upper'] - bb['lower'])) * 100 if bb['upper'] != bb['lower'] else 50
                
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
        
        with col2:
            st.markdown("##### 🎯 Support & Resistance")
            if result.get('support_resistance'):
                sr = result['support_resistance']
                
                # Current price vs S/R
                st.markdown("**Level Penting:**")
                
                levels = []
                if 'recent_high' in sr:
                    levels.append(('🔼 Resistance', sr['recent_high']))
                if 'recent_low' in sr:
                    levels.append(('🔽 Support', sr['recent_low']))
                
                for name, value in levels:
                    diff_pct = ((value - result['current_price']) / result['current_price'] * 100)
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
                        diff_pct = ((level - result['current_price']) / result['current_price'] * 100)
                        st.markdown(f"- {format_currency(level)} ({format_percentage(diff_pct)})")
        
        # Trading scenarios
        st.markdown("---")
        st.markdown("##### 📈 Trading Scenarios")
        
        try:
            if st.session_state.predictor:
                # Create dummy dataframe for scenarios
                dummy_data = pd.DataFrame({
                    'Close': [result['current_price']] * 30,
                    'High': [result['current_price'] * 1.05] * 30,
                    'Low': [result['current_price'] * 0.95] * 30
                })
                
                scenarios = st.session_state.predictor.generate_trading_scenarios(dummy_data)
                
                if scenarios and 'bullish_scenario' in scenarios:
                    cols = st.columns(3)
                    scenario_configs = {
                        'bullish_scenario': ('🟢', '#10B981', 'BULLISH'),
                        'bearish_scenario': ('🔴', '#EF4444', 'BEARISH'),
                        'sideways_scenario': ('🟡', '#F59E0B', 'SIDEWAYS')
                    }
                    
                    for idx, (scenario_name, scenario_data) in enumerate(scenarios.items()):
                        if scenario_name in scenario_configs:
                            emoji, color, title = scenario_configs[scenario_name]
                            
                            with cols[idx % 3]:
                                st.markdown(f'<div style="background-color: {color}20; padding: 15px; border-radius: 10px; border-left: 5px solid {color}; margin-bottom: 15px;">', unsafe_allow_html=True)
                                st.markdown(f"**{emoji} {title}**")
                                st.markdown(f"*Probabilitas: {scenario_data.get('probability', 'N/A')}*")
                                
                                if 'target' in scenario_data:
                                    st.markdown(f"**Target:** {format_currency(scenario_data['target'])}")
                                
                                if 'stop_loss' in scenario_data:
                                    st.markdown(f"**Stop Loss:** {format_currency(scenario_data['stop_loss'])}")
                                
                                if 'risk' in scenario_data:
                                    risk_color = "#EF4444" if 'High' in scenario_data['risk'] else "#F59E0B" if 'Medium' in scenario_data['risk'] else "#10B981"
                                    st.markdown(f'<span style="color: {risk_color};">**Risk:** {scenario_data["risk"]}</span>', unsafe_allow_html=True)
                                
                                if 'description' in scenario_data:
                                    st.caption(scenario_data['description'])
                                
                                st.markdown('</div>', unsafe_allow_html=True)
        except Exception as e:
            st.info("⚠️ Trading scenarios tidak tersedia untuk analisis ini")
    
    with tab4:
        # Information tab
        st.subheader("📋 Informasi Detail")
        
        # Data grid
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("##### 🔧 Parameter Prediksi")
            info_data = {
                'Ticker': result['ticker'],
                'Sumber Data Harga': result.get('price_source', 'N/A'),
                'Jumlah Data Historis': f"{result.get('data_points', 0)} points",
                'Tanggal Data Terakhir': result.get('latest_data_date', 'N/A'),
                'Prediction Days': len(result['predictions']),
                'Max Daily Change': "±3%",
                'Confidence Algorithm': "Conservative Mean Reversion"
            }
            
            for key, value in info_data.items():
                st.markdown(f"**{key}:** {value}")
        
        with col2:
            st.markdown("##### ⚙️ System Info")
            sys_data = {
                'Waktu Pemrosesan': f"{result.get('processing_time', 0)} detik",
                'Cache Digunakan': "✅ Ya" if result.get('cache_used') else "❌ Tidak",
                'Harga Real-time': "✅ Digunakan" if result.get('realtime_price_used', False) else "❌ Tidak tersedia",
                'Model yang Digunakan': "Volatility Random Walk",
                'Mean Reversion Factor': "30%"
            }
            
            for key, value in sys_data.items():
                st.markdown(f"**{key}:** {value}")
        
        # Performance metrics
        st.markdown("##### 📊 Performance Metrics")
        perf_cols = st.columns(4)
        
        with perf_cols[0]:
            st.metric("Volatility", f"{result['volatility_pct']}%")
        with perf_cols[1]:
            st.metric("Confidence", f"{result['confidence']}%")
        with perf_cols[2]:
            st.metric("Trend Strength", f"{abs(result['trend_percentage']):.1f}%")
        with perf_cols[3]:
            cache_status = "HIT" if result.get('cache_used') else "MISS"
            st.metric("Cache Status", cache_status)
        
        # Disclaimer
        st.markdown("---")
        st.markdown("##### ⚠️ PERINGATAN & DISCLAIMER")
        
        st.markdown("""
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
        
        st.markdown(f"<small>{result.get('disclaimer', '')}</small>", unsafe_allow_html=True)

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
            st.success("✅ Predictor initialized successfully!")
        except Exception as e:
            st.error(f"❌ Gagal menginisialisasi predictor: {str(e)}")
            st.info("Pastikan file price_predictor.py ada di folder ai/")
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
                        st.write("Available methods:", dir(st.session_state.predictor))
    
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

def stock_screener_panel():
    """Panel untuk stock screener"""
    st.title("📊 Stock Screener")
    st.info("Fitur Stock Screener akan segera hadir!")
    
    # Placeholder content
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 🔍 Filter Saham")
        st.multiselect(
            "Sektor:",
            ["Finance", "Consumer", "Energy", "Infrastructure", "Property"],
            default=["Finance"]
        )
        
        st.slider(
            "Market Cap (Rp Triliun):",
            min_value=0.0,
            max_value=1000.0,
            value=(10.0, 500.0)
        )
        
        st.slider(
            "ROE (%):",
            min_value=0.0,
            max_value=50.0,
            value=(10.0, 30.0)
        )
    
    with col2:
        st.markdown("### 📈 Hasil Screening")
        st.dataframe(
            pd.DataFrame({
                'Ticker': ['BBCA.JK', 'BBRI.JK', 'BMRI.JK', 'TLKM.JK', 'ASII.JK'],
                'Nama': ['Bank BCA', 'Bank BRI', 'Bank Mandiri', 'Telkom', 'Astra'],
                'Sektor': ['Finance', 'Finance', 'Finance', 'Infra', 'Consumer'],
                'Market Cap': ['1,200T', '800T', '600T', '400T', '300T'],
                'ROE': ['18.5%', '16.2%', '15.8%', '12.3%', '14.7%']
            }),
            use_container_width=True
        )

def portfolio_panel():
    """Panel untuk portfolio management"""
    st.title("📋 Portfolio Management")
    st.info("Fitur Portfolio Management akan segera hadir!")
    
    # Placeholder content
    st.markdown("### 💼 Portofolio Anda")
    
    portfolio_data = pd.DataFrame({
        'Ticker': ['BBCA.JK', 'BBRI.JK', 'TLKM.JK'],
        'Jumlah': [100, 200, 150],
        'Harga Beli': [9500, 4500, 3500],
        'Harga Sekarang': [9800, 4600, 3600],
        'Untung/Rugi': ['+3.16%', '+2.22%', '+2.86%'],
        'Nilai': ['980M', '920M', '540M']
    })
    
    st.dataframe(portfolio_data, use_container_width=True)
    
    total_value = 2440  # in millions
    st.metric("Total Nilai Portofolio", f"Rp {total_value:,.0f}M")

def settings_panel():
    """Panel untuk settings"""
    st.title("⚙️ Settings")
    
    st.markdown("### 🛠️ Konfigurasi Aplikasi")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### 📊 Display Settings")
        st.checkbox("Dark Mode", value=False)
        st.selectbox("Theme", ["Light", "Dark", "Auto"])
        st.slider("Font Size", 12, 24, 16)
    
    with col2:
        st.markdown("#### 🔗 Data Sources")
        st.checkbox("Yahoo Finance", value=True)
        st.checkbox("IDX Data", value=True)
        st.checkbox("Google Finance", value=False)
    
    st.markdown("### 💾 Cache Management")
    
    col1, col2 = st.columns(2)
    
    with col1:
        cache_size = st.session_state.predictor.data_cache.__sizeof__() if st.session_state.predictor else 0
        st.metric("Cache Size", f"{cache_size:,} bytes")
    
    with col2:
        if st.button("Clear All Cache", type="secondary"):
            if st.session_state.predictor:
                st.session_state.predictor.clear_cache()
                st.success("Cache cleared!")

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
            stock_screener_panel()
        elif app_mode == "📋 Portfolio":
            portfolio_panel()
        else:  # Settings
            settings_panel()
            
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
