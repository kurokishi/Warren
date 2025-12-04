import streamlit as st
import yfinance as yf
import pandas as pd

st.title("Test Yahoo Finance")

ticker = st.text_input("Ticker", "BBCA.JK")

if st.button("Test"):
    try:
        stock = yf.Ticker(ticker)
        df = stock.history(period="1mo")
        
        if df.empty:
            st.error("Data kosong!")
        else:
            st.success(f"Success! Data shape: {df.shape}")
            st.dataframe(df.head())
            
            info = stock.info
            st.json({k: info[k] for k in ['symbol', 'shortName', 'trailingPE'] if k in info})
            
    except Exception as e:
        st.error(f"Error: {str(e)}")
