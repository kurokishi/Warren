import streamlit as st
from core.data_loader import DataLoader
from core.fundamental import FundamentalEngine
from core.technical import TechnicalEngine
from core.dividend import DividendEngine
from core.scoring import ScoringEngine

from ai.hybrid_explainer import HybridAIExplainer
from ai.confidence import ConfidenceEngine
from ai.risk import RiskDisclosureEngine
from ai.scenario import ScenarioEngine
from ai.stress import StressTestEngine
from ai.compliance import ComplianceEngine


class StockAnalyzer:
    def __init__(self, ticker: str, period="1y"):
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
            # Load data
            df, stock = self.loader.load(self.ticker)
            info = stock.info

            # Core analysis
            fund_result = self.fund.analyze(info)
            tech_result = self.tech.calculate(df)
            div_result = self.div.analyze(info)

            # Calculate scores
            final_score = self.score_engine.final_score(
                fund_result.get("FundamentalScore", 0),
                tech_result.get("TechnicalRating", {}).get("Raw", 0)
            )
            label = self.score_engine.label(final_score)

            # Build result
            result = {
                "Ticker": self.ticker,
                **fund_result,
                **tech_result,
                "DividendYield": div_result.get("Yield"),
                "FinalScore": final_score,
                "Label": label,
            }

            # AI Explanation
            ai_explanation = self.ai.explain(result)
            result.update({
                "AI_Rule": ai_explanation.get("rule_based", ""),
                "AI_LLM": ai_explanation.get("llm_explanation", ""),
                "AI_Final": ai_explanation.get("hybrid", ""),
                "Confidence": self.confidence.calculate(result),
                "Risks": self.risk_engine.generate(result),
            })

            # Scenario analysis
            scenarios = self.scenario.run(result)
            result.update({
                "Scenarios": scenarios,
                "ResilienceScore": self.stress.score(scenarios),
                "Disclaimer": self.compliance.generate({
                    "user_type": "retail",
                    "horizon": "medium"
                })
            })

            return result

        except Exception as e:
            return {
                "Ticker": self.ticker,
                "Error": str(e),
                "FinalScore": 0,
                "Label": "ERROR",
                "AI_Final": f"Analysis failed: {str(e)}",
                "Confidence": 0,
                "Risks": [f"Analysis error: {str(e)}"],
                "Scenarios": {},
                "ResilienceScore": 0,
                "Disclaimer": "Analysis unavailable due to error."
            }
