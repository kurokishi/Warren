class FundamentalEngine:
    def analyze(self, info: dict) -> dict:
        try:
            pe = info.get("trailingPE")
            pbv = info.get("priceToBook")
            roe = info.get("returnOnEquity")
            
            # Handle missing/None values
            if pe is None or not isinstance(pe, (int, float)):
                pe = 20.0  # Default value
            if pbv is None or not isinstance(pbv, (int, float)):
                pbv = 2.5  # Default value
            if roe is None or not isinstance(roe, (int, float)):
                roe = 0.1  # Default value
            
            score = 0
            if pe < 15: score += 2
            elif pe < 25: score += 1
            
            if pbv < 2: score += 2
            elif pbv < 3: score += 1
            
            if roe > 0.15: score += 2
            elif roe > 0.08: score += 1

            return {
                "PER": round(float(pe), 2),
                "PBV": round(float(pbv), 2),
                "ROE": round(float(roe), 4),
                "FundamentalScore": score
            }
        except Exception as e:
            return {
                "PER": 20.0,
                "PBV": 2.5,
                "ROE": 0.1,
                "FundamentalScore": 3
            }
