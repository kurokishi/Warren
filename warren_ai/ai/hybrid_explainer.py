from warren_ai.ai.explanation import AIExplanationEngine
from warren_ai.ai.llm_client import LLMClient


class HybridAIExplainer:
    """
    Hybrid AI = Rule-based facts + optional LLM narrative
    """

    def __init__(self):
        self.rule_engine = AIExplanationEngine()
        self.llm = LLMClient()

    def explain(self, result: dict) -> dict:
        rule_text = self.rule_engine.explain(result)

        prompt = f"""
You are preparing an equity research summary.

Rewrite the explanation below into a concise,
professional analyst-style paragraph.

Rules:
- Do NOT add any numbers
- Do NOT make forecasts
- Do NOT change BUY/HOLD/AVOID stance
- Use neutral, investment research tone

Explanation:
{rule_text}
"""

        llm_text = self.llm.generate(prompt)

        return {
            "rule_based": rule_text,
            "llm_explanation": llm_text,
            "hybrid": llm_text if llm_text else rule_text,
        }
