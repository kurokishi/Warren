import os
import sys
import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from datetime import datetime, timedelta
import time

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
    }
    .stTabs [aria-selected="true"] {
        background-color: #3B82F6 !important;
        color: white !important;
    }
    .stock-badge {
        display: inline-block;
        background: #3B82F6;
        color: white;
        padding: 4px 12px;
        border-radius: 20px;
        font-size: 0.9rem;
        font-weight: 600;
        margin: 2px;
    }
    .refresh-button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important;
        color: white !important;
        border: none !important;
        font-weight: 600 !important;
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
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'last_ticker' not in st.session_state:
    st.session_state.last_ticker = None
if 'prediction_history' not in st.session_state:
    st.session_state.prediction_history = []
if 'auto_refresh' not in st.session_state:
    st.session_state.auto_refresh = False
if 'predictor' not in st.session_state:
    st.session_state.predictor = None

# Initialize predictor
@st.cache_resource
def init_predictor():
    try:
        from ai.price_predictor import ConservativePricePredictor
        predictor = ConservativePricePredictor()
        print("✅ Predictor initialized successfully")
        return predictor
    except Exception as e:
        st.error(f"❌ Failed to initialize predictor: {str(e)}")
        return None

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

def create_price_chart(predictions, current_price, ticker):
    """Create interactive price prediction chart"""
    days = list(range(len(predictions) + 1))
    prices = [current_price] + predictions
    
    fig = go.Figure()
    
    # Add current price point
    fig.add_trace(go.Scatter(
        x=[0], 
        y=[current_price],
        mode='markers',
        name='Harga Saat Ini',
        marker=dict(
            size=15,
            color='#3B82F6',
            symbol='star',
            line=dict(width=2, color='white')
        )
    ))
    
    # Add prediction line
    fig.add_trace(go.Scatter(
        x=days, 
        y=prices,
        mode='lines+markers',
        name='Prediksi',
        line=dict(color='#10B981', width=4),
        marker=dict(size=10, color='#10B981')
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
            showlegend=True
        ))
    
    # Update layout
    fig.update_layout(
        title=f"Prediksi Harga {ticker}",
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
            bgcolor='rgba(255, 255, 255, 0.9)'
        ),
        plot_bgcolor='rgba(240, 240, 240, 0.5)',
        paper_bgcolor='rgba(255, 255, 255, 0.1)'
    )
    
    # Add grid
    fig.update_xaxes(showgrid=True, gridwidth=1, gridcolor='lightgray')
    fig.update_yaxes(showgrid=True, gridwidth=1, gridcolor='lightgray')
    
    return fig

def display_prediction_results(result, ticker):
    """Display prediction results in a nice format"""
    
    if result.get('error'):
        st.error(f"❌ {result['message']}")
        return
    
    # Header dengan ticker dan timestamp
    col1, col2 = st.columns([3, 1])
    with col1:
        st.markdown(f"### 📊 Analisis Teknis & Prediksi: **{ticker}**")
    with col2:
        st.caption(f"Terakhir diperbarui: {datetime.now().strftime('%H:%M:%S')}")
    
    # Key metrics dalam 4 kolom
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        st.metric(
            label="HARGA SAAT INI",
            value=format_currency(result['current_price']),
            delta=format_percentage(result['potential_change_pct']),
            delta_color="normal"
        )
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col2:
        # Determine trend color class
        trend_class = "trend-neutral"
        if "bullish" in result['trend']:
            trend_class = "trend-up"
        elif "bearish" in result['trend']:
            trend_class = "trend-down"
        
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        st.metric(
            label="TREND PREDIKSI",
            value=f"{result['trend_icon']} {result['trend'].upper()}",
            delta=f"{result['trend_percentage']}%"
        )
        st.markdown(f'<p class="{trend_class}">{result["trend_icon"]} {result["trend"]}</p>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col3:
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        
        # Confidence bar
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
        
        st.markdown(f"**CONFIDENCE LEVEL**")
        st.markdown(f"### {confidence}%")
        st.markdown(f'<small>{label}</small>', unsafe_allow_html=True)
        
        # Progress bar
        st.progress(confidence / 100)
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col4:
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        st.metric(
            label="VOLATILITAS",
            value=f"{result['volatility_pct']}%",
            help="Volatilitas harian historis"
        )
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
            
            pred_data.append({
                'HARI': f'H+{i+1}',
                'TANGGAL': (datetime.now() + timedelta(days=i+1)).strftime('%d %b'),
                'PREDIKSI HARGA': format_currency(price),
                'PERUBAHAN': change_pct,
                'VS KEMARIN': ((price - result['predictions'][i-1]) / result['predictions'][i-1] * 100) if i > 0 else 0
            })
        
        df_pred = pd.DataFrame(pred_data)
        
        # Format dataframe dengan styling
        styled_df = df_pred.style.format({
            'PERUBAHAN': lambda x: f"{'↗️ ' if x >= 0 else '↘️ '}{format_percentage(x)}",
            'VS KEMARIN': lambda x: f"{'📈 ' if x >= 0 else '📉 '}{format_percentage(x)}"
        })
        
        # Apply background gradient untuk perubahan
        styled_df = styled_df.background_gradient(
            subset=['PERUBAHAN'],
            cmap='RdYlGn',
            vmin=-5,
            vmax=5
        )
        
        st.dataframe(styled_df, use_container_width=True, hide_index=True)
        
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
                label="Rata-rata 5 Hari",
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
        st.subheader("Visualisasi Prediksi")
        
        fig = create_price_chart(result['predictions'], result['current_price'], ticker)
        st.plotly_chart(fig, use_container_width=True)
        
        # Range realistis dengan gauge chart
        st.subheader("📊 Range Realistis 5 Hari")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            optimistic = result['realistic_range']['optimistic']
            optimistic_pct = ((optimistic - result['current_price']) / result['current_price'] * 100)
            
            fig_opt = go.Figure(go.Indicator(
                mode="number+delta",
                value=optimistic,
                number={'prefix': "Rp ", 'valueformat': ",.0f"},
                delta={'reference': result['current_price'], 'relative': True, 'valueformat': '.1%'},
                title={'text': "SCENARIO OPTIMISTIS", 'font': {'size': 14}},
                domain={'row': 0, 'column': 0}
            ))
            
            fig_opt.update_layout(
                height=200,
                paper_bgcolor='rgba(0,0,0,0)',
                font={'color': "green"}
            )
            st.plotly_chart(fig_opt, use_container_width=True)
        
        with col2:
            most_likely = result['realistic_range']['most_likely']
            most_likely_pct = ((most_likely - result['current_price']) / result['current_price'] * 100)
            
            fig_mid = go.Figure(go.Indicator(
                mode="number+delta",
                value=most_likely,
                number={'prefix': "Rp ", 'valueformat': ",.0f"},
                delta={'reference': result['current_price'], 'relative': True, 'valueformat': '.1%'},
                title={'text': "PALING MUNGKIN", 'font': {'size': 14}},
                domain={'row': 0, 'column': 0}
            ))
            
            fig_mid.update_layout(
                height=200,
                paper_bgcolor='rgba(0,0,0,0)',
                font={'color': "blue"}
            )
            st.plotly_chart(fig_mid, use_container_width=True)
        
        with col3:
            pessimistic = result['realistic_range']['pessimistic']
            pessimistic_pct = ((pessimistic - result['current_price']) / result['current_price'] * 100)
            
            fig_pes = go.Figure(go.Indicator(
                mode="number+delta",
                value=pessimistic,
                number={'prefix': "Rp ", 'valueformat': ",.0f"},
                delta={'reference': result['current_price'], 'relative': True, 'valueformat': '.1%'},
                title={'text': "SCENARIO PESIMISTIS", 'font': {'size': 14}},
                domain={'row': 0, 'column': 0}
            ))
            
            fig_pes.update_layout(
                height=200,
                paper_bgcolor='rgba(0,0,0,0)',
                font={'color': "red"}
            )
            st.plotly_chart(fig_pes, use_container_width=True)
    
    with tab3:
        # Technical analysis
        st.subheader("Analisis Teknis Mendalam")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("##### 📊 Bollinger Bands Analysis")
            if result.get('bollinger_bands'):
                bb = result['bollinger_bands']
                
                # Create gauge for position in bands
                current_price = result['current_price']
                position_pct = ((current_price - bb['lower']) / (bb['upper'] - bb['lower'])) * 100 if bb['upper'] != bb['lower'] else 50
                
                fig_bb = go.Figure(go.Indicator(
                    mode="gauge+number",
                    value=position_pct,
                    title={'text': "Posisi dalam Bollinger Band"},
                    gauge={
                        'axis': {'range': [0, 100]},
                        'bar': {'color': "darkblue"},
                        'steps': [
                            {'range': [0, 20], 'color': "lightgreen"},
                            {'range': [20, 80], 'color': "lightyellow"},
                            {'range': [80, 100], 'color': "lightcoral"}
                        ],
                        'threshold': {
                            'line': {'color': "red", 'width': 4},
                            'thickness': 0.75,
                            'value': position_pct
                        }
                    }
                ))
                
                fig_bb.update_layout(height=300)
                st.plotly_chart(fig_bb, use_container_width=True)
                
                # Band info
                st.markdown("**Detail Bollinger Bands:**")
                st.write(f"- **Upper Band:** {format_currency(bb['upper'])}")
                st.write(f"- **Middle Band (MA20):** {format_currency(bb['middle'])}")
                st.write(f"- **Lower Band:** {format_currency(bb['lower'])}")
                st.write(f"- **Band Width:** {bb['width_pct']:.1f}%")
                
                # Interpretation
                if position_pct > 80:
                    st.warning("⚠️ **OVERBOUGHT**: Harga mendekati resistance, potensi koreksi")
                elif position_pct < 20:
                    st.info("ℹ️ **OVERSOLD**: Harga mendekati support, potensi rebound")
                else:
                    st.success("✅ **NORMAL**: Harga dalam range normal")
        
        with col2:
            st.markdown("##### 🎯 Support & Resistance")
            if result.get('support_resistance'):
                sr = result['support_resistance']
                
                st.markdown("**Level Penting:**")
                
                # Create mini chart for S/R
                levels = []
                if 'recent_high' in sr:
                    levels.append(('Resistance', sr['recent_high']))
                if 'recent_low' in sr:
                    levels.append(('Support', sr['recent_low']))
                if 'current' in sr:
                    levels.append(('Current', sr['current']))
                
                for name, value in levels:
                    diff_pct = ((value - result['current_price']) / result['current_price'] * 100)
                    arrow = "↑" if diff_pct > 0 else "↓"
                    st.write(f"- **{name}:** {format_currency(value)} ({arrow} {abs(diff_pct):.1f}%)")
                
                # Psychological levels
                if 'psychological_levels' in sr:
                    st.markdown("**Level Psikologis:**")
                    for level in sr['psychological_levels']:
                        diff_pct = ((level - result['current_price']) / result['current_price'] * 100)
                        st.write(f"  • {format_currency(level)} ({format_percentage(diff_pct)})")
        
        # Trading scenarios
        st.markdown("---")
        st.markdown("##### 📈 Trading Scenarios")
        
        # Generate scenarios
        try:
            from ai.price_predictor import ConservativePricePredictor
            predictor = ConservativePricePredictor()
            
            # Create dummy dataframe for scenarios
            dummy_data = pd.DataFrame({
                'Close': [result['current_price']] * 30,
                'High': [result['current_price'] * 1.05] * 30,
                'Low': [result['current_price'] * 0.95] * 30
            })
            
            scenarios = predictor.generate_trading_scenarios(dummy_data)
            
            if 'bullish_scenario' in scenarios:
                cols = st.columns(3)
                scenario_colors = {
                    'bullish_scenario': ('🟢', '#10B981'),
                    'bearish_scenario': ('🔴', '#EF4444'),
                    'sideways_scenario': ('🟡', '#F59E0B')
                }
                
                for idx, (scenario_name, scenario_data) in enumerate(scenarios.items()):
                    with cols[idx % 3]:
                        emoji, color = scenario_colors.get(scenario_name, ('🔵', '#3B82F6'))
                        
                        st.markdown(f'<div style="background-color: {color}20; padding: 15px; border-radius: 10px; border-left: 5px solid {color}">', unsafe_allow_html=True)
                        st.markdown(f"**{emoji} {scenario_name.replace('_', ' ').upper()}**")
                        st.markdown(f"*Probabilitas: {scenario_data.get('probability', 'N/A')}*")
                        st.markdown(f"**Target:** {format_currency(scenario_data.get('target', 0))}")
                        st.markdown(f"**Risk:** {scenario_data.get('risk', 'N/A')}")
                        st.markdown('</div>', unsafe_allow_html=True)
        except:
            st.info("Trading scenarios tidak tersedia untuk analisis ini")
    
    with tab4:
        # Information tab
        st.subheader("📋 Informasi Detail Prediksi")
        
        # Data grid
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("##### 🔧 Parameter Prediksi")
            info_data = {
                'Ticker': result['ticker'],
                'Sumber Data Harga': result.get('price_source', 'N/A'),
                'Jumlah Data Historis': f"{result.get('data_points', 0)} points",
                'Tanggal Data Terakhir': result.get('latest_data_date', 'N/A'),
                'Prediction Days': len(result['predictions'])
            }
            
            for key, value in info_data.items():
                st.markdown(f"**{key}:** {value}")
        
        with col2:
            st.markdown("##### ⚙️ System Info")
            sys_data = {
                'Waktu Pemrosesan': f"{result.get('processing_time', 0)} detik",
                'Cache Digunakan': "✅ Ya" if result.get('cache_used') else "❌ Tidak",
                'Harga Real-time': "✅ Digunakan" if result.get('realtime_price_used') else "❌ Tidak tersedia",
                'Confidence Algorithm': "Conservative Mean Reversion",
                'Max Daily Change': "±3%"
            }
            
            for key, value in sys_data.items():
                st.markdown(f"**{key}:** {value}")
        
        # Disclaimer
        st.markdown("---")
        st.markdown("##### ⚠️ PERINGATAN & DISCLAIMER")
        
        st.markdown("""
        <div class="warning-box">
        <h5>PENTING: BACA SEBELUM MENGGUNAKAN PREDIKSI INI</h5>
        
        1. **BUKAN REKOMENDASI INVESTASI** - Prediksi ini bersifat informatif dan edukatif belaka<br>
        2. **AKURASI TIDAK DIJAMIN** - Prediksi didasarkan pada model probabilistik dengan margin error<br>
        3. **RISIKO INVESTASI** - Saham mengandung risiko, nilai dapat naik atau turun<br>
        4. **LITERASI KEUANGAN** - Pastikan Anda memahami produk investasi sebelum berinvestasi<br>
        5. **DIVERSIFIKASI** - Jangan menaruh semua modal dalam satu saham<br>
        6. **KONSULTASI PROFESIONAL** - Konsultasikan dengan penasihat keuangan bersertifikat<br>
        7. **PAST PERFORMANCE** - Tidak menjamin future performance<br>
        
        <strong>Investasi yang bijak adalah investasi yang terinformasi dengan baik!</strong>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown(f"<small>{result['disclaimer']}</small>", unsafe_allow_html=True)

def price_prediction_panel():
    """Panel utama untuk prediksi harga"""
    st.markdown('<h2 class="main-title">📈 AI STOCK PRICE PREDICTOR</h2>', unsafe_allow_html=True)
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
                if st.button(name, use_container_width=True):
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
            
            st.markdown("**🎯 VOLATILITY SETTINGS:**")
            volatility_adjust = st.slider(
                "Adjust Volatility Factor:",
                min_value=0.5,
                max_value=2.0,
                value=1.0,
                step=0.1,
                help="Faktor penyesuaian volatilitas"
            )
        
        # Action buttons
        st.markdown("---")
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("🔄 CLEAR CACHE", use_container_width=True):
                if st.session_state.predictor:
                    st.session_state.predictor.clear_cache()
                st.session_state.last_ticker = None
                st.success("Cache cleared!")
                time.sleep(1)
                st.rerun()
        
        with col2:
            if st.button("📊 VIEW HISTORY", use_container_width=True):
                st.session_state.show_history = True
    
    # Main content area
    if not ticker or ticker == ".JK":
        st.warning("⚠️ Silakan masukkan ticker saham di sidebar")
        return
    
    # Initialize predictor jika belum ada
    if st.session_state.predictor is None:
        st.session_state.predictor = init_predictor()
    
    if st.session_state.predictor is None:
        st.error("❌ Gagal menginisialisasi predictor. Mohon cek koneksi dan dependencies.")
        return
    
    # Check if ticker changed
    if ticker != st.session_state.last_ticker:
        st.session_state.last_ticker = ticker
        st.session_state.predictor.clear_cache(ticker)
        
        # Show loading message
        with st.spinner(f"🔄 Memuat data baru untuk {ticker}..."):
            time.sleep(1)  # Small delay for visual feedback
    
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
    if predict_button:
        with st.spinner(f"🔍 Menganalisis {ticker}..."):
            try:
                # Get prediction
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
                    st.write("**Predictor:**", st.session_state.predictor)
    
    # Show prediction history if requested
    if st.session_state.get('show_history', False) and st.session_state.prediction_history:
        st.markdown("---")
        st.markdown("### 📜 RIWAYAT PREDIKSI")
        
        for i, entry in enumerate(st.session_state.prediction_history[:10]):
            with st.container():
                col1, col2, col3, col4 = st.columns([2, 2, 2, 1])
                
                with col1:
                    st.markdown(f"**{entry['ticker']}**")
                
                with col2:
                    st.markdown(f"`{entry['timestamp']}`")
                
                with col3:
                    if not entry['result'].get('error'):
                        trend = entry['result'].get('trend', 'N/A')
                        icon = entry['result'].get('trend_icon', '')
                        st.markdown(f"{icon} **{trend}**")
                
                with col4:
                    if not entry['result'].get('error'):
                        price = entry['result'].get('current_price', 0)
                        st.markdown(f"**{format_currency(price)}**")
                
                if i < len(st.session_state.prediction_history[:10]) - 1:
                    st.divider()
        
        if st.button("Tutup Riwayat"):
            st.session_state.show_history = False
            st.rerun()

def main():
    try:
        # Main navigation
        st.sidebar.markdown("## 🧭 NAVIGASI")
        
        # App mode selection
        app_mode = st.sidebar.radio(
            "Pilih Mode Aplikasi:",
            ["📈 Price Prediction", "📊 Stock Screener", "📋 Portfolio", "⚙️ Settings"],
            index=0
        )
        
        st.sidebar.markdown("---")
        st.sidebar.markdown("### 📊 MARKET INFO")
        
        # Display market status
        market_status = "🟢 BURSA BUKA" if 9 <= datetime.now().hour < 16 else "🔴 BURSA TUTUP"
        st.sidebar.markdown(f"**Status:** {market_status}")
        st.sidebar.markdown(f"**Waktu:** {datetime.now().strftime('%H:%M:%S')}")
        
        # Run selected mode
        if app_mode == "📈 Price Prediction":
            price_prediction_panel()
        elif app_mode == "📊 Stock Screener":
            try:
                from ui.screener_panel import screener_panel
                screener_panel()
            except Exception as e:
                st.error(f"Stock Screener Error: {str(e)}")
                st.info("Modul Stock Screener belum tersedia.")
        elif app_mode == "📋 Portfolio":
            st.title("Portfolio Management")
            st.info("Fitur Portfolio Management akan segera hadir!")
        else:  # Settings
            st.title("Settings")
            st.info("Pengaturan aplikasi akan segera hadir!")
            
    except Exception as e:
        st.error(f"❌ Application Error: {str(e)}")
        
        # Debug information
        with st.expander("🐛 Debug Information"):
            st.write("**Error details:**", str(e))
            st.write("**Current directory:**", os.getcwd())
            st.write("**Python path:**", sys.path)
            
            # List available files
            st.write("**Available files in root:**")
            for item in os.listdir('.'):
                st.write(f"- {item}")
            
            # Check for ai module
            if os.path.exists('./ai'):
                st.write("**Files in ai folder:**")
                for item in os.listdir('./ai'):
                    st.write(f"  - {item}")

if __name__ == "__main__":
    main()
