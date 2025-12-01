class DividendEngine:
    def analyze(self, info: dict) -> dict:
        dy = info.get("dividendYield", 0)
        if dy and dy > 10:  # Handle percentage conversion
            dy = dy / 100
        return {"Yield": dy}
