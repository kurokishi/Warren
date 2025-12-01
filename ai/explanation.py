class AIExplanationEngine:
    def explain(self, result: dict) -> str:
        lines = []

        ticker = result.get("Ticker")
        label = result.get("Label")
        score = result.get("FinalScore")

        lines.append(f"📌 **{ticker} — {label}**")
        lines.append(f"Skor keseluruhan: **{score}**")

        # Fundamental analysis
        per = result.get("PER")
        pbv = result.get("PBV")
        roe = result.get("ROE")

        fund_notes = []
        if isinstance(per, (int, float)):
            if per < 15:
                fund_notes.append("valuasi PER tergolong murah")
            else:
                fund_notes.append("PER relatif tinggi")

        if isinstance(pbv, (int, float)):
            if pbv < 2:
                fund_notes.append("PBV masih menarik")
            else:
                fund_notes.append("PBV sudah cukup mahal")

        if isinstance(roe, (int, float)):
            if roe > 0.15:
                fund_notes.append("ROE kuat menandakan efisiensi manajemen")
            else:
                fund_notes.append("ROE tergolong rendah")

        if fund_notes:
            lines.append("🔎 **Fundamental:** " + ", ".join(fund_notes) + ".")

        # Technical analysis
        rsi = result.get("RSI")
        macd = result.get("MACD")

        tech_notes = []
        if isinstance(rsi, (int, float)):
            if rsi < 30:
                tech_notes.append("RSI oversold (potensi rebound)")
            elif rsi < 50:
                tech_notes.append("RSI netral")
            else:
                tech_notes.append("RSI mendekati overbought")

        if isinstance(macd, (int, float)):
            if macd > 0:
                tech_notes.append("momentum MACD positif")

        if tech_notes:
            lines.append("📈 **Teknikal:** " + ", ".join(tech_notes) + ".")

        # Dividend analysis
        dy = result.get("DividendYield")
        if isinstance(dy, (int, float)) and dy > 0:
            lines.append(f"💰 **Dividen:** dividend yield sekitar {dy*100:.2f}%.")

        # Conclusion
        if label in ("BUY", "STRONG BUY"):
            lines.append(
                "✅ Saham ini layak diperhatikan untuk **akumulasi bertahap**, "
                "terutama bagi investor jangka menengah–panjang."
            )
        elif label == "HOLD":
            lines.append(
                "⚖️ Saham ini lebih cocok **dipantau** sambil menunggu konfirmasi lanjutan."
            )
        else:
            lines.append(
                "⛔ Risiko relatif lebih tinggi, **tidak direkomendasikan** saat ini."
            )

        return "\n\n".join(lines)
