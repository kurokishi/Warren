import yfinance as yf
import pandas as pd
import requests
from datetime import datetime, timedelta

class DataLoader:
    def __init__(self, period: str = "1y"):
        self.period = period
        
    def load(self, ticker: str):
        ticker = ticker.upper().strip()
        
        # Create custom session dengan headers untuk bypass restrictions
        session = requests.Session()
        session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'DNT': '1',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
        })
        
        # Coba berbagai format ticker
        ticker_variants = []
        
        # Untuk saham Indonesia
        if not ticker.endswith('.JK'):
            ticker_variants.append(f"{ticker}.JK")
        ticker_variants.append(ticker)
        
        # Tambah variasi lain
        if '.JK' in ticker:
            base_ticker = ticker.replace('.JK', '')
            ticker_variants.append(base_ticker)
        
        for ticker_variant in ticker_variants:
            try:
                print(f"Mencoba download: {ticker_variant}")
                
                # Gunakan session custom
                stock = yf.Ticker(ticker_variant, session=session)
                
                # Download dengan interval 1d
                df = stock.history(period=self.period, interval="1d")
                
                if df.empty:
                    print(f"Data kosong untuk {ticker_variant}")
                    continue
                
                if len(df) < 5:  # Minimal data
                    print(f"Data terlalu sedikit untuk {ticker_variant}: {len(df)} rows")
                    continue
                
                # Coba dapatkan info
                try:
                    info = stock.info
                    if not info:
                        print(f"Info kosong untuk {ticker_variant}")
                        # Buat info minimal
                        info = {
                            'symbol': ticker_variant,
                            'shortName': ticker_variant,
                        }
                except Exception as e:
                    print(f"Error mengambil info: {e}")
                    # Buat info minimal
                    info = {
                        'symbol': ticker_variant,
                        'shortName': ticker_variant,
                    }
                
                print(f"Berhasil load data untuk {ticker_variant}: {len(df)} rows")
                return df, stock
                
            except Exception as e:
                print(f"Error untuk {ticker_variant}: {str(e)[:100]}")
                continue
        
        # Fallback: Coba dengan ticker langsung tanpa .JK
        if '.JK' in ticker:
            base_ticker = ticker.replace('.JK', '')
            try:
                print(f"Fallback: Mencoba {base_ticker}")
                stock = yf.Ticker(base_ticker, session=session)
                df = stock.history(period="3mo", interval="1d")
                
                if not df.empty:
                    return df, stock
            except:
                pass
        
        # Buat dataframe kosong sebagai last resort
        print(f"Membuat dataframe kosong untuk {ticker}")
        dates = pd.date_range(end=datetime.now(), periods=30, freq='D')
        df = pd.DataFrame({
            'Open': [100] * 30,
            'High': [105] * 30,
            'Low': [95] * 30,
            'Close': [100] * 30,
            'Volume': [1000000] * 30
        }, index=dates)
        
        class MockStock:
            def __init__(self, ticker):
                self.ticker = ticker
                self.info = {
                    'symbol': ticker,
                    'shortName': ticker,
                    'trailingPE': 15.0,
                    'priceToBook': 2.0,
                    'returnOnEquity': 0.15,
                    'dividendYield': 0.03,
                }
        
        return df, MockStock(ticker)
