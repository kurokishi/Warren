class ScenarioEngine:
    def run(self, result: dict) -> dict:
        scenarios = {}

        # Technical sensitivity proxy
        tech_score = result.get("TechnicalRating", {}).get("Raw", 0)
        fund_score = result.get("FundamentalScore", 0)

        # Market crash
        crash_impact = -max(1, tech_score)
        scenarios["Market Crash"] = {
            "impact": crash_impact,
            "comment": "Tekanan jual tinggi, saham defensif lebih tahan."
        }

        # Bull market
        scenarios["Bull Market"] = {
            "impact": tech_score + 1,
            "comment": "Momentum positif berpotensi memperkuat tren."
        }

        # Rate hike
        rate_impact = -2 if result.get("PBV", 0) > 3 else -1
        scenarios["Rate Hike"] = {
            "impact": rate_impact,
            "comment": "Kenaikan suku bunga menekan valuasi."
        }

        # Earnings shock
        earn_impact = -2 if result.get("ROE", 0) < 0.1 else -1
        scenarios["Earnings Shock"] = {
            "impact": earn_impact,
            "comment": "Penurunan laba berdampak ke sentimen."
        }

        return scenarios
