import yfinance as yf
import pandas as pd


class DataLoader:
    def __init__(self, period: str = "2y"):
        self.period = period

    def load(self, ticker: str):
        ticker = ticker.upper().strip()
        symbols = [f"{ticker}.JK", ticker]

        for sym in symbols:
            stock = yf.Ticker(sym)
            df = stock.history(period=self.period)
            if not df.empty:
                return df, stock

        raise ValueError(f"Data tidak ditemukan untuk {ticker}")
