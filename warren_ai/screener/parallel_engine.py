import multiprocessing as mp
import pandas as pd
from warren_ai.models.stock import StockAnalyzer


def _worker(ticker):
    return StockAnalyzer(ticker).analyze()


class ParallelScreener:
    def __init__(self, workers=4):
        self.workers = workers

    def run(self, tickers):
        with mp.Pool(self.workers) as p:
            rows = p.map(_worker, tickers)
        return pd.DataFrame(rows)
