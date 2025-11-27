import ta


class TechnicalEngine:
    def calculate(self, df):
        close = df["Close"]

        rsi = ta.momentum.RSIIndicator(close).rsi().iloc[-1]
        macd = ta.trend.MACD(close).macd_diff().iloc[-1]

        score = 0
        if rsi < 30: score += 2
        elif rsi < 50: score += 1

        if macd > 0: score += 2

        return {
            "RSI": round(rsi, 2),
            "MACD": round(macd, 2),
            "TechnicalRating": {
                "Raw": score
            }
        }
