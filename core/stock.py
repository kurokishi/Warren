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

import time

class StockAnalyzer:
    def __init__(self, ticker: str, period="3mo"):
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
        start_time = time.time()
        
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

            # Build result dengan default values
            result = {
                "Ticker": self.ticker,
                **fund_result,
                **tech_result,
                "DividendYield": div_result.get("Yield", 0),
                "FinalScore": final_score,
                "Label": label,
            }

            # AI Explanation
            try:
                ai_explanation = self.ai.explain(result)
                result.update({
                    "AI_Rule": ai_explanation.get("rule_based", "No rule-based explanation available"),
                    "AI_LLM": ai_explanation.get("llm_explanation", ""),
                    "AI_Final": ai_explanation.get("hybrid", ai_explanation.get("rule_based", "No analysis available")),
                })
            except Exception as ai_error:
                result.update({
                    "AI_Rule": "AI explanation failed",
                    "AI_LLM": "",
                    "AI_Final": f"Analysis completed with limited AI insights. Error: {str(ai_error)[:100]}",
                })

            # Confidence score
            try:
                result["Confidence"] = self.confidence.calculate(result)
            except:
                result["Confidence"] = 50  # Default

            # Risks
            try:
                result["Risks"] = self.risk_engine.generate(result)
            except:
                result["Risks"] = ["Risk analysis not available"]

            # Scenario analysis
            try:
                scenarios = self.scenario.run(result)
                result.update({
                    "Scenarios": scenarios,
                    "ResilienceScore": self.stress.score(scenarios),
                })
            except:
                result.update({
                    "Scenarios": {},
                    "ResilienceScore": 50,  # Default
                })

            # Compliance
            try:
                result["Disclaimer"] = self.compliance.generate({
                    "user_type": "retail",
                    "horizon": "medium"
                })
            except:
                result["Disclaimer"] = "Standard disclaimer: For educational purposes only."

            result["AnalysisTime"] = round(time.time() - start_time, 2)

            return result

        except Exception as e:
            return {
                "Ticker": self.ticker,
                "Error": str(e),
                "FinalScore": 0,
                "Label": "ERROR",
                "AI_Final": f"Analysis failed: {str(e)[:100]}",
                "Confidence": 0,
                "Risks": [f"Error during analysis: {str(e)[:100]}"],
                "Scenarios": {},
                "ResilienceScore": 0,
                "Disclaimer": "Analysis unavailable due to technical error.",
                "AnalysisTime": round(time.time() - start_time, 2)
            }
