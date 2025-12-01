import yfinance as yf
import pandas as pd

class DataLoader:
    def __init__(self, period: str = "1y"):
        self.period = period

    def load(self, ticker: str):
        ticker = ticker.upper().strip()
        
        # Try different suffix combinations for Indonesian stocks
        symbols = [
            f"{ticker}.JK",  # Indonesian format
            ticker,          # Plain ticker
            f"{ticker}.NS",  # NSE India (backup)
            f"{ticker}.AX"   # ASX Australia (backup)
        ]

        for sym in symbols:
            try:
                stock = yf.Ticker(sym)
                df = stock.history(period=self.period)
                if not df.empty and len(df) > 10:
                    return df, stock
            except Exception:
                continue

        raise ValueError(f"Data tidak ditemukan untuk {ticker}")
