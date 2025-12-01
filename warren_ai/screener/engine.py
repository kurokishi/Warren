import pandas as pd
import streamlit as st

class ScreenerEngine:
    def analyze_batch(self, tickers: list) -> pd.DataFrame:
        results = []
        for ticker in tickers:
            try:
                # Import here to avoid circular imports
                from warren_ai.core.stock import StockAnalyzer
                
                analyzer = StockAnalyzer(ticker)
                result = analyzer.analyze()
                results.append(result)
            except Exception as e:
                st.error(f"Error analyzing {ticker}: {str(e)}")
                # Add placeholder for failed analysis
                results.append({
                    "Ticker": ticker,
                    "Error": str(e),
                    "FinalScore": 0,
                    "Label": "ERROR"
                })
        
        return pd.DataFrame(results)
