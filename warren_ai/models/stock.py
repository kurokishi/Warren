from warren_ai.core.data_loader import DataLoader
from warren_ai.core.fundamental import FundamentalEngine
from warren_ai.core.technical import TechnicalEngine
from warren_ai.core.dividend import DividendEngine
from warren_ai.core.scoring import ScoringEngine


class StockAnalyzer:
    def __init__(self, ticker: str, period="2y"):
        self.ticker = ticker
        self.loader = DataLoader(period)
        self.fund = FundamentalEngine()
        self.tech = TechnicalEngine()
        self.div = DividendEngine()
        self.score_engine = ScoringEngine()

    def analyze(self):
        df, stock = self.loader.load(self.ticker)
        info = stock.info

        fund = self.fund.analyze(info)
        tech = self.tech.calculate(df)
        div = self.div.analyze(info)

        final_score = self.score_engine.final_score(
            fund["FundamentalScore"],
            tech["TechnicalRating"]["Raw"],
        )

        return {
            "Ticker": self.ticker,
            **fund,
            **tech,
            "DividendYield": div["Yield"],
            "FinalScore": final_score,
            "Label": self.score_engine.label(final_score),
        }
