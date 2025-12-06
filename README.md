# WarrenAI - AI Stock Analysis & Prediction

Aplikasi prediksi harga saham berbasis AI untuk pasar Indonesia dengan pendekatan konservatif.

## 🚀 Fitur Utama

### 📈 Price Prediction
- Prediksi harga saham untuk 1-10 hari ke depan
- Analisis teknis dengan Bollinger Bands
- Support & Resistance levels
- Trading scenarios dengan probabilitas
- Grafik interaktif dengan Plotly

### 📊 Real-time Data
- Data real-time dari Yahoo Finance
- Auto-refresh setiap request
- Cache management untuk performa
- Error handling yang robust

### 🎨 User Interface
- Dashboard yang modern dan responsif
- Multiple tabs untuk organisasi konten
- Metric cards dengan visualisasi
- Dark/light mode ready

## 📁 Struktur Project
warren/
├── app_streamlit.py
├── requirements.txt
├── core/
│   ├── __init__.py
│   ├── data_loader.py
│   ├── fundamental.py
│   ├── technical.py
│   ├── dividend.py
│   ├── scoring.py
│   └── stock.py
├── ai/
│   ├── __init__.py
│   ├── hybrid_explainer.py
│   ├── confidence.py
│   ├── risk.py
│   ├── scenario.py
│   ├── stress.py
│   ├── compliance.py
│   ├── explanation.py
│   └── llm_client.py
├── screener/
│   ├── __init__.py
│   ├── engine.py
│   └── parallel_engine.py
└── ui/
    ├── __init__.py
    └── screener_panel.py
