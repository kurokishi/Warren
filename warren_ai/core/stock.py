from warren_ai.core.data_loader import DataLoader
from warren_ai.core.fundamental import FundamentalEngine
from warren_ai.core.technical import TechnicalEngine
from warren_ai.core.dividend import DividendEngine
from warren_ai.core.scoring import ScoringEngine

from warren_ai.ai.hybrid_explainer import HybridAIExplainer
from warren_ai.ai.confidence import ConfidenceEngine
from warren_ai.ai.risk import RiskDisclosureEngine
from warren_ai.ai.scenario import ScenarioEngine
from warren_ai.ai.stress import StressTestEngine
from warren_ai.ai.compliance import ComplianceEngine


class StockAnalyzer:
    def __init__(self, ticker: str, period="2y"):
        self.ticker = ticker
        self.loader = DataLoader(period)

        # Core engines
        self.fund = FundamentalEngine()
        self.tech = TechnicalEngine()
        self.div = DividendEngine()
        self.score_engine = ScoringEngine()

        # AI engines
        self.ai = HybridAIExplainer()
        self.confidence = ConfidenceEngine()
        self.risk_engine = RiskDisclosureEngine()
        self.scenario = ScenarioEngine()
        self.stress = StressTestEngine()
        self.compliance = ComplianceEngine()

    def analyze(self):
        try:
            df, stock = self.loader.load(self.ticker)
            info = stock.info

            # Core analysis
            fund = self.fund.analyze(info)
            tech = self.tech.calculate(df)
            div = self.div.analyze(info)

            final_score = self.score_engine.final_score(
                fund.get("FundamentalScore", 0),
                tech.get("TechnicalRating", {}).get("Raw", 0),
            )

            label = self.score_engine.label(final_score)

            # Result object
            result = {
                "Ticker": self.ticker,
                **fund,
                **tech,
                "DividendYield": div.get("Yield"),
                "FinalScore": final_score,
                "Label": label,
            }

            # AI Explanation
            ai_explanation = self.ai.explain(result)
            result["AI_Rule"] = ai_explanation.get("rule_based", "")
            result["AI_LLM"] = ai_explanation.get("llm_explanation", "")
            result["AI_Final"] = ai_explanation.get("hybrid", "")

            # Additional analysis
            result["Confidence"] = self.confidence.calculate(result)
            result["Risks"] = self.risk_engine.generate(result)
            
            scenarios = self.scenario.run(result)
            result["Scenarios"] = scenarios
            result["ResilienceScore"] = self.stress.score(scenarios)
            
            # Compliance
            result["Disclaimer"] = self.compliance.generate({
                "user_type": "retail",
                "horizon": "medium",
            })

            return result

        except Exception as e:
            # Return error result
            return {
                "Ticker": self.ticker,
                "Error": str(e),
                "FinalScore": 0,
                "Label": "ERROR",
                "AI_Final": f"Analysis failed: {str(e)}",
                "Confidence": 0,
                "Risks": ["Analysis failed - unable to process stock data"],
                "Scenarios": {},
                "ResilienceScore": 0,
                "Disclaimer": "Analysis unavailable due to error."
            }
