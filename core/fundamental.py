class FundamentalEngine:
    def analyze(self, info: dict) -> dict:
        try:
            pe = info.get("trailingPE")
            pbv = info.get("priceToBook")
            roe = info.get("returnOnEquity")
            
            # Ensure numeric values
            pe = float(pe) if pe is not None and pd.notna(pe) else 20.0
            pbv = float(pbv) if pbv is not None and pd.notna(pbv) else 2.5
            roe = float(roe) if roe is not None and pd.notna(roe) else 0.12
            
            # Clamp values to reasonable ranges
            pe = max(0.1, min(pe, 100))
            pbv = max(0.1, min(pbv, 10))
            roe = max(-1.0, min(roe, 1.0))
            
            score = 0
            if pe < 15: score += 2
            elif pe < 25: score += 1
            
            if pbv < 2: score += 2
            elif pbv < 3: score += 1
            
            if roe > 0.15: score += 2
            elif roe > 0.08: score += 1

            return {
                "PER": round(pe, 2),
                "PBV": round(pbv, 2),
                "ROE": round(roe, 4),
                "FundamentalScore": score
            }
        except Exception as e:
            # Return safe default values
            return {
                "PER": 20.0,
                "PBV": 2.5,
                "ROE": 0.12,
                "FundamentalScore": 3
            }
