class FundamentalEngine:
    def analyze(self, info: dict) -> dict:
        pe = info.get("trailingPE")
        pbv = info.get("priceToBook")
        roe = info.get("returnOnEquity")

        score = 0
        if pe and pe < 15: score += 2
        elif pe and pe < 25: score += 1
        
        if pbv and pbv < 2: score += 2
        elif pbv and pbv < 3: score += 1
        
        if roe and roe > 0.15: score += 2
        elif roe and roe > 0.08: score += 1

        return {
            "PER": pe,
            "PBV": pbv,
            "ROE": roe,
            "FundamentalScore": score
        }
