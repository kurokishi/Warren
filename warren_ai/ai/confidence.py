class ConfidenceEngine:
    """
    Produces confidence level (0–100) based on signal quality.
    """

    def calculate(self, result: dict) -> int:
        score = result.get("FinalScore", 0)

        confidence = 30  # baseline

        # Strength of score
        if score >= 7:
            confidence += 35
        elif score >= 5:
            confidence += 25
        elif score >= 3:
            confidence += 15

        # Fundamental confirmation
        if result.get("ROE") and result["ROE"] > 0.15:
            confidence += 10

        # Technical confirmation
        if result.get("MACD") and result["MACD"] > 0:
            confidence += 10

        # Data penalty
        missing = sum(
            result.get(k) is None
            for k in ("PER", "PBV", "ROE", "RSI")
        )
        confidence -= missing * 5

        return max(10, min(100, confidence))
