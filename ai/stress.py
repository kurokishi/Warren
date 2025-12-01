class StressTestEngine:
    def score(self, scenarios: dict) -> int:
        base = 70

        for s in scenarios.values():
            base += s["impact"] * 5

        return max(10, min(100, base))
