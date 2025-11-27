from warren_ai.core.data_loader import DataLoader
from warren_ai.core.fundamental import FundamentalEngine
from warren_ai.core.technical import TechnicalEngine
from warren_ai.core.dividend import DividendEngine
from warren_ai.core.scoring import ScoringEngine

from warren_ai.ai.hybrid_explainer import HybridAIExplainer


class StockAnalyzer:
    def __init__(self, ticker: str, period="2y"):
        self.ticker = ticker
        self.loader = DataLoader(period)

        self.fund = FundamentalEngine()
        self.tech = TechnicalEngine()
        self.div = DividendEngine()
        self.score_engine = ScoringEngine()

        # ✅ INIT AI HYBRID EXPLAINER
        self.ai = HybridAIExplainer()

    def analyze(self):
        df, stock = self.loader.load(self.ticker)
        info = stock.info

        # === CORE ANALYSIS ===
        fund = self.fund.analyze(info)
        tech = self.tech.calculate(df)
        div = self.div.analyze(info)

        final_score = self.score_engine.final_score(
            fund["FundamentalScore"],
            tech["TechnicalRating"]["Raw"],
        )

        label = self.score_engine.label(final_score)

        # ✅ RESULT OBJECT
        result = {
            "Ticker": self.ticker,
            **fund,
            **tech,
            "DividendYield": div["Yield"],
            "FinalScore": final_score,
            "Label": label,
        }

        # === ✅ HYBRID AI EXPLANATION ===
        ai_explanation = self.ai.explain(result)

        result["AI_Rule"] = ai_explanation["rule_based"]
        result["AI_LLM"] = ai_explanation["llm_explanation"]
        result["AI_Final"] = ai_explanation["hybrid"]

        return result

