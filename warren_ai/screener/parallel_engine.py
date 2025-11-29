import pandas as pd
from warren_ai.core.stock import StockAnalyzer
import concurrent.futures

class ParallelScreener:
    def run(self, tickers: list) -> pd.DataFrame:
        def analyze_ticker(ticker):
            try:
                analyzer = StockAnalyzer(ticker)
                return analyzer.analyze()
            except Exception as e:
                print(f"Error analyzing {ticker}: {e}")
                return None
        
        results = []
        with concurrent.futures.ThreadPoolExecutor() as executor:
            futures = [executor.submit(analyze_ticker, ticker) for ticker in tickers]
            for future in concurrent.futures.as_completed(futures):
                result = future.result()
                if result:
                    results.append(result)
        
        return pd.DataFrame(results)
