class ScoringEngine:
    def final_score(self, fund, tech):
        return fund + tech

    def label(self, score: int):
        if score >= 7:
            return "STRONG BUY"
        if score >= 5:
            return "BUY"
        if score >= 3:
            return "HOLD"
        return "AVOID"
