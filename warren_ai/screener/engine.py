import pandas as pd
from warren_ai.models.stock import StockAnalyzer


class ScreenerEngine:
    def analyze_batch(self, tickers: list[str]) -> pd.DataFrame:
        rows = []
        for t in tickers:
            try:
                rows.append(StockAnalyzer(t).analyze())
            except Exception:
                continue
        return pd.DataFrame(rows)
