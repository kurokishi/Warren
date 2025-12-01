class RiskDisclosureEngine:
    def generate(self, result: dict) -> list[str]:
        risks = []

        # Valuation risk
        if result.get("PER") and result["PER"] > 25:
            risks.append("Valuasi relatif tinggi (PER di atas rata-rata).")

        # Profitability risk
        if result.get("ROE") and result["ROE"] < 0.1:
            risks.append("Profitabilitas rendah (ROE di bawah 10%).")

        # Technical risk
        if result.get("RSI") and result["RSI"] > 70:
            risks.append("Harga berpotensi jenuh beli (RSI tinggi).")

        # Dividend risk
        if not result.get("DividendYield"):
            risks.append("Tidak ada atau dividen tidak signifikan.")

        # Generic
        if not risks:
            risks.append("Risiko utama berasal dari kondisi pasar secara umum.")

        return risks
