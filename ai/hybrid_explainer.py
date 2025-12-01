from ai.explanation import AIExplanationEngine
from ai.llm_client import LLMClient

class HybridAIExplainer:
    def __init__(self):
        self.rule_engine = AIExplanationEngine()
        self.llm = LLMClient()

    def explain(self, result: dict) -> dict:
        rule_text = self.rule_engine.explain(result)

        # Try LLM explanation, fallback to rule-based
        try:
            llm_text = self.llm.generate(rule_text)
        except:
            llm_text = None

        return {
            "rule_based": rule_text,
            "llm_explanation": llm_text,
            "hybrid": llm_text if llm_text else rule_text,
        }
