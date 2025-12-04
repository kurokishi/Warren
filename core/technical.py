import pandas as pd
import numpy as np

class TechnicalEngine:
    def calculate(self, df):
        try:
            if df.empty or len(df) < 20:
                return self._get_default_result()
            
            close = df["Close"].astype(float)
            
            # Calculate RSI manually (fallback jika TA-Lib error)
            def calculate_rsi(prices, period=14):
                deltas = np.diff(prices)
                seed = deltas[:period+1]
                up = seed[seed >= 0].sum()/period
                down = -seed[seed < 0].sum()/period
                rs = up/down
                rsi = np.zeros_like(prices)
                rsi[:period] = 100. - 100./(1.+rs)
                
                for i in range(period, len(prices)):
                    delta = deltas[i-1]
                    if delta > 0:
                        upval = delta
                        downval = 0.
                    else:
                        upval = 0.
                        downval = -delta
                    
                    up = (up*(period-1) + upval)/period
                    down = (down*(period-1) + downval)/period
                    rs = up/down
                    rsi[i] = 100. - 100./(1.+rs)
                
                return rsi[-1]
            
            # Calculate MACD manually
            def calculate_macd(prices):
                exp1 = prices.ewm(span=12, adjust=False).mean()
                exp2 = prices.ewm(span=26, adjust=False).mean()
                macd = exp1 - exp2
                signal = macd.ewm(span=9, adjust=False).mean()
                return macd.iloc[-1] - signal.iloc[-1]
            
            # Calculate indicators
            rsi_value = calculate_rsi(close.values)
            macd_value = calculate_macd(close)
            
            # Handle NaN
            rsi_value = 50 if pd.isna(rsi_value) else rsi_value
            macd_value = 0 if pd.isna(macd_value) else macd_value
            
            # Calculate score
            score = 0
            if rsi_value < 30: score += 2
            elif rsi_value < 50: score += 1

            if macd_value > 0: score += 2

            return {
                "RSI": round(float(rsi_value), 2),
                "MACD": round(float(macd_value), 4),
                "TechnicalRating": {"Raw": score}
            }
            
        except Exception as e:
            return self._get_default_result()
    
    def _get_default_result(self):
        return {
            "RSI": 50.0,
            "MACD": 0.0,
            "TechnicalRating": {"Raw": 1}
        }
