import pandas as pd

class ScreenerEngine:
    def analyze_batch(self, tickers: list) -> pd.DataFrame:
        results = []
        for ticker in tickers:
            try:
                from core.stock import StockAnalyzer
                analyzer = StockAnalyzer(ticker)
                result = analyzer.analyze()
                results.append(result)
            except Exception as e:
                # Add error result
                results.append({
                    "Ticker": ticker,
                    "Error": str(e),
                    "FinalScore": 0,
                    "Label": "ERROR"
                })
        
        return pd.DataFrame(results)
