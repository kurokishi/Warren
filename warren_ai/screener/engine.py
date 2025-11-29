import pandas as pd
from warren_ai.core.stock import StockAnalyzer

class ScreenerEngine:
    def analyze_batch(self, tickers: list) -> pd.DataFrame:
        results = []
        for ticker in tickers:
            try:
                analyzer = StockAnalyzer(ticker)
                result = analyzer.analyze()
                results.append(result)
            except Exception as e:
                print(f"Error analyzing {ticker}: {e}")
                continue
        
        return pd.DataFrame(results)
