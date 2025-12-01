import pandas as pd
import concurrent.futures

class ParallelScreener:
    def run(self, tickers: list) -> pd.DataFrame:
        def analyze_ticker(ticker):
            try:
                from core.stock import StockAnalyzer
                analyzer = StockAnalyzer(ticker)
                return analyzer.analyze()
            except Exception as e:
                return {
                    "Ticker": ticker,
                    "Error": str(e),
                    "FinalScore": 0,
                    "Label": "ERROR"
                }
        
        results = []
        with concurrent.futures.ThreadPoolExecutor(max_workers=3) as executor:
            future_to_ticker = {
                executor.submit(analyze_ticker, ticker): ticker 
                for ticker in tickers
            }
            
            for future in concurrent.futures.as_completed(future_to_ticker):
                result = future.result()
                if result:
                    results.append(result)
        
        return pd.DataFrame(results)
