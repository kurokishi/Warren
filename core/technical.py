import pandas as pd
try:
    import talib
    TA_AVAILABLE = True
except ImportError:
    TA_AVAILABLE = False

class TechnicalEngine:
    def calculate(self, df):
        if df.empty or len(df) < 20:
            return {
                "RSI": 50,
                "MACD": 0,
                "TechnicalRating": {"Raw": 0}
            }
            
        close = df["Close"]

        try:
            # Calculate RSI
            if TA_AVAILABLE:
                rsi = talib.RSI(close, timeperiod=14).iloc[-1]
                macd_line = talib.MACD(close)[0].iloc[-1]
            else:
                # Fallback calculation
                delta = close.diff()
                gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
                loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
                rs = gain / loss
                rsi = 100 - (100 / (1 + rs)).iloc[-1]
                
                exp1 = close.ewm(span=12).mean()
                exp2 = close.ewm(span=26).mean()
                macd_line = (exp1 - exp2).iloc[-1]
            
            # Handle NaN values
            rsi = 50 if pd.isna(rsi) else rsi
            macd_line = 0 if pd.isna(macd_line) else macd_line

            score = 0
            if rsi < 30: score += 2
            elif rsi < 50: score += 1

            if macd_line > 0: score += 2

            return {
                "RSI": round(rsi, 2),
                "MACD": round(macd_line, 4),
                "TechnicalRating": {"Raw": score}
            }
        except Exception as e:
            return {
                "RSI": 50,
                "MACD": 0,
                "TechnicalRating": {"Raw": 0}
            }
