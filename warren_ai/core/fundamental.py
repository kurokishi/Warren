class FundamentalEngine:
    def analyze(self, info: dict) -> dict:
        pe = info.get("trailingPE")
        pbv = info.get("priceToBook")
        roe = info.get("returnOnEquity")

        score = 0
        if pe and pe < 15: score += 2
        if pbv and pbv < 2: score += 2
        if roe and roe > 0.15: score += 2

        return {
            "PER": pe,
            "PBV": pbv,
            "ROE": roe,
            "FundamentalScore": score
        }
