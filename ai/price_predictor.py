import pandas as pd
import numpy as np
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import StandardScaler
import warnings
warnings.filterwarnings('ignore')

class ConservativePricePredictor:
    """
    CONSERVATIVE price prediction based on historical volatility
    - Maximum daily change: ±3% (realistic for blue chips)
    - Uses Bollinger Bands for realistic range
    - Emphasizes mean reversion
    - Clear disclaimer about limitations
    """
    
    def __init__(self):
        self.model = LinearRegression()
        self.scaler = StandardScaler()
        
        # Conservative parameters for Indonesian blue chips
        self.MAX_DAILY_CHANGE = 0.03  # Max 3% daily change (realistic)
        self.VOLATILITY_WINDOW = 20   # Lookback for volatility calculation
        self.CONFIDENCE_DECAY = 0.8   # Confidence decays over prediction horizon
    
    def calculate_historical_volatility(self, df):
        """Calculate realistic historical volatility"""
        if len(df) < 10:
            return 0.015  # Default 1.5% volatility
        
        returns = df['Close'].pct_change().dropna()
        if len(returns) < 5:
            return 0.015
        
        # Use rolling standard deviation
        volatility = returns.rolling(window=min(10, len(returns))).std().iloc[-1]
        
        # Cap volatility at reasonable levels
        return min(max(volatility, 0.005), 0.05)  # Between 0.5% and 5%
    
    def calculate_bollinger_bands(self, df, window=20):
        """Calculate Bollinger Bands for realistic price ranges"""
        if len(df) < window:
            return None, None, None
        
        rolling_mean = df['Close'].rolling(window=window).mean()
        rolling_std = df['Close'].rolling(window=window).std()
        
        upper_band = rolling_mean + (2 * rolling_std)
        lower_band = rolling_mean - (2 * rolling_std)
        
        return {
            'upper': float(upper_band.iloc[-1]),
            'middle': float(rolling_mean.iloc[-1]),
            'lower': float(lower_band.iloc[-1]),
            'width_pct': float((upper_band.iloc[-1] - lower_band.iloc[-1]) / rolling_mean.iloc[-1] * 100)
        }
    
    def get_support_resistance_levels(self, df):
        """Identify key support and resistance levels"""
        if len(df) < 20:
            return {'support': 0, 'resistance': 0}
        
        # Simple approach: recent highs and lows
        recent_high = df['High'].tail(20).max()
        recent_low = df['Low'].tail(20).min()
        current = df['Close'].iloc[-1]
        
        # Psychological levels (round numbers)
        def find_psychological_levels(price):
            # Round to nearest 50, 100, 500
            levels = []
            base = round(price / 100) * 100
            levels.extend([base - 200, base - 100, base, base + 100, base + 200])
            return [l for l in levels if l > 0]
        
        psych_levels = find_psychological_levels(current)
        
        return {
            'recent_high': float(recent_high),
            'recent_low': float(recent_low),
            'current': float(current),
            'psychological_levels': psych_levels[:3]  # Top 3 nearest
        }
    
    def predict_with_volatility_model(self, df, days=5):
        """Predict using volatility-based random walk with mean reversion"""
        if len(df) < 30:
            return self._get_ultra_conservative_prediction(df)
        
        current_price = df['Close'].iloc[-1]
        volatility = self.calculate_historical_volatility(df)
        
        # Calculate Bollinger Bands
        bb = self.calculate_bollinger_bands(df)
        
        # Get support/resistance
        sr_levels = self.get_support_resistance_levels(df)
        
        # Generate predictions with mean reversion
        predictions = []
        last_price = current_price
        
        for day in range(days):
            # Mean reversion factor (prices tend to revert to mean)
            if bb:
                mean_reversion_factor = 0.3 * (bb['middle'] - last_price) / bb['middle']
            else:
                mean_reversion_factor = 0
            
            # Random component based on historical volatility
            random_component = np.random.normal(0, volatility) * 0.7  # Reduced randomness
            
            # Combined daily change (capped)
            daily_change = mean_reversion_factor + random_component
            daily_change = max(-self.MAX_DAILY_CHANGE, min(self.MAX_DAILY_CHANGE, daily_change))
            
            next_price = last_price * (1 + daily_change)
            
            # Apply support/resistance boundaries
            if sr_levels['recent_high'] and next_price > sr_levels['recent_high'] * 1.02:
                next_price = sr_levels['recent_high'] * 0.98  # Resistance bounce
            
            if sr_levels['recent_low'] and next_price < sr_levels['recent_low'] * 0.98:
                next_price = sr_levels['recent_low'] * 1.02  # Support bounce
            
            predictions.append(next_price)
            last_price = next_price
        
        # Calculate trend (very conservative)
        avg_prediction = np.mean(predictions)
        trend_percentage = (avg_prediction - current_price) / current_price * 100
        
        if abs(trend_percentage) < 0.5:
            trend = "sideways"
        elif trend_percentage > 0:
            trend = "slightly bullish"
        else:
            trend = "slightly bearish"
        
        # Confidence decays with prediction horizon
        confidence = max(30, 70 * (self.CONFIDENCE_DECAY ** (days-1)))
        
        return {
            'current_price': round(float(current_price), 2),
            'predictions': [round(float(p), 2) for p in predictions],
            'next_day_prediction': round(float(predictions[0]), 2),
            'trend': trend,
            'confidence': round(float(confidence), 1),
            'potential_change_pct': round(((predictions[0] - current_price) / current_price * 100), 2),
            'avg_prediction': round(float(avg_prediction), 2),
            'volatility_pct': round(volatility * 100, 2),
            'bollinger_bands': bb,
            'support_resistance': sr_levels,
            'realistic_range': {
                'optimistic': round(current_price * 1.05, 2),  # Max +5% in 5 days
                'pessimistic': round(current_price * 0.95, 2), # Max -5% in 5 days
                'most_likely': round(np.median(predictions), 2)
            },
            'disclaimer': "Prediksi didasarkan pada volatilitas historis. Pergerakan aktual bisa berbeda. Gunakan hanya sebagai referensi tambahan."
        }
    
    def _get_ultra_conservative_prediction(self, df):
        """Ultra conservative prediction when data is limited"""
        if len(df) == 0:
            current_price = 0
        else:
            current_price = df['Close'].iloc[-1]
        
        # Simple mean reversion prediction
        if len(df) >= 5:
            ma_5 = df['Close'].rolling(5).mean().iloc[-1]
            # Very small mean reversion
            if current_price > ma_5 * 1.02:
                next_price = current_price * 0.995  # Slight correction
                trend = "slight correction"
            elif current_price < ma_5 * 0.98:
                next_price = current_price * 1.005  # Slight rebound
                trend = "slight rebound"
            else:
                next_price = current_price
                trend = "sideways"
        else:
            next_price = current_price
            trend = "sideways"
        
        predictions = [next_price] * 5
        
        return {
            'current_price': round(float(current_price), 2),
            'predictions': [round(float(p), 2) for p in predictions],
            'next_day_prediction': round(float(next_price), 2),
            'trend': trend,
            'confidence': 40,  # Low confidence due to limited data
            'potential_change_pct': 0.0,
            'avg_prediction': round(float(current_price), 2),
            'volatility_pct': 1.5,
            'bollinger_bands': None,
            'support_resistance': {'current': current_price},
            'realistic_range': {
                'optimistic': round(current_price * 1.03, 2),
                'pessimistic': round(current_price * 0.97, 2),
                'most_likely': round(current_price, 2)
            },
            'disclaimer': "Prediksi sangat konservatif karena data terbatas. Tidak direkomendasikan untuk keputusan investasi."
        }
    
    def generate_trading_scenarios(self, df):
        """Generate realistic trading scenarios instead of precise predictions"""
        if len(df) < 20:
            return self._get_basic_scenarios(df)
        
        current_price = df['Close'].iloc[-1]
        volatility = self.calculate_historical_volatility(df)
        bb = self.calculate_bollinger_bands(df)
        
        scenarios = {
            'bullish_scenario': {
                'probability': '30%',
                'description': 'Breakout atas dengan volume tinggi',
                'target': round(current_price * (1 + volatility * 3), 2),
                'stop_loss': round(current_price * (1 - volatility * 2), 2),
                'condition': 'Volume > rata-rata 20 hari',
                'risk': 'Medium-High'
            },
            'bearish_scenario': {
                'probability': '25%',
                'description': 'Koreksi menuju support',
                'target': round(current_price * (1 - volatility * 2.5), 2),
                'stop_loss': round(current_price * (1 + volatility * 1.5), 2),
                'condition': 'RSI > 70 dan MACD negatif',
                'risk': 'Medium'
            },
            'sideways_scenario': {
                'probability': '45%',
                'description': 'Konsolidasi dalam range',
                'range': {
                    'upper': round(current_price * (1 + volatility * 1.5), 2),
                    'lower': round(current_price * (1 - volatility * 1.5), 2)
                },
                'strategy': 'Range trading',
                'risk': 'Low'
            }
        }
        
        return scenarios
    
    def _get_basic_scenarios(self, df):
        """Basic scenarios when data is limited"""
        if len(df) == 0:
            current_price = 0
        else:
            current_price = df['Close'].iloc[-1]
        
        return {
            'conservative_advice': {
                'message': 'Data tidak cukup untuk analisis teknis mendalam',
                'recommendation': 'Tunggu konfirmasi lebih lanjut',
                'suggested_action': 'Monitor dan tunggu setup yang jelas',
                'risk_level': 'High (karena ketidakpastian)'
            }
        }
