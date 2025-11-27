class DividendEngine:
    def analyze(self, info: dict) -> dict:
        dy = info.get("dividendYield")
        return {"Yield": dy}
