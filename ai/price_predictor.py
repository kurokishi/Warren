import pandas as pd
import numpy as np
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import StandardScaler
import warnings
warnings.filterwarnings('ignore')

# Import yfinance untuk data real-time
try:
    import yfinance as yf
    YFINANCE_AVAILABLE = True
except ImportError:
    YFINANCE_AVAILABLE = False
    print("Warning: yfinance not installed. Install with: pip install yfinance")

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
        
        # Cache untuk menyimpan data real-time
        self.price_cache = {}
        self.cache_timeout = 300  # 5 menit
    
    def get_realtime_price(self, ticker):
        """
        Get real-time price from Yahoo Finance for Indonesian stocks
        """
        if not YFINANCE_AVAILABLE:
            return None
            
        try:
            # Clean ticker symbol
            ticker_clean = ticker.upper().replace('.JK', '') + '.JK'
            
            # Check cache first
            current_time = pd.Timestamp.now()
            if ticker_clean in self.price_cache:
                cached_price, cached_time = self.price_cache[ticker_clean]
                if (current_time - cached_time).seconds < self.cache_timeout:
                    return cached_price
            
            # Get stock data from yfinance
            stock = yf.Ticker(ticker_clean)
            
            # Try multiple methods to get current price
            current_price = None
            
            # Method 1: Try currentPrice from info
            info = stock.info
            current_price = info.get('currentPrice')
            
            # Method 2: Try regularMarketPrice
            if current_price is None:
                current_price = info.get('regularMarketPrice')
            
            # Method 3: Try from last close with today's data
            if current_price is None:
                # Get today's intraday data
                hist = stock.history(period='1d', interval='1m')
                if not hist.empty:
                    current_price = hist['Close'].iloc[-1]
            
            # Method 4: Get latest daily close
            if current_price is None:
                hist = stock.history(period='5d')
                if not hist.empty:
                    current_price = hist['Close'].iloc[-1]
            
            if current_price is not None and not np.isnan(current_price):
                # Update cache
                self.price_cache[ticker_clean] = (current_price, current_time)
                return float(current_price)
            
            return None
            
        except Exception as e:
            print(f"Error getting real-time price for {ticker}: {e}")
            return None
    
    def update_dataframe_with_realtime(self, df, ticker):
        """
        Update dataframe with the latest real-time data
        """
        if not YFINANCE_AVAILABLE or df.empty:
            return df
            
        try:
            ticker_clean = ticker.upper().replace('.JK', '') + '.JK'
            stock = yf.Ticker(ticker_clean)
            
            # Get today's data
            today_data = stock.history(period='1d')
            
            if not today_data.empty:
                latest = today_data.iloc[-1]
                latest_date = today_data.index[-1]
                
                # Check if we already have today's data
                if len(df) > 0 and df.index[-1].date() == latest_date.date():
                    # Update last row with today's actual data
                    df.iloc[-1] = {
                        'Close': latest['Close'],
                        'High': max(df['High'].iloc[-1], latest['High']) if 'High' in df.columns else latest['High'],
                        'Low': min(df['Low'].iloc[-1], latest['Low']) if 'Low' in df.columns else latest['Low'],
                        'Open': latest['Open'] if 'Open' in df.columns else latest['Open'],
                        'Volume': latest['Volume'] if 'Volume' in df.columns else latest['Volume']
                    }
                else:
                    # Add new row for today
                    new_row = pd.DataFrame({
                        'Close': [latest['Close']],
                        'High': [latest['High']],
                        'Low': [latest['Low']],
                        'Open': [latest['Open']] if 'Open' in df.columns else [latest['Open']],
                        'Volume': [latest['Volume']] if 'Volume' in df.columns else [latest['Volume']]
                    }, index=[latest_date])
                    
                    df = pd.concat([df, new_row])
            
            return df
            
        except Exception as e:
            print(f"Error updating dataframe: {e}")
            return df
    
    def calculate_historical_volatility(self, df):
        """Calculate realistic historical volatility"""
        if len(df) < 10:
            return 0.015  # Default 1.5% volatility
        
        if 'Close' not in df.columns:
            return 0.015
            
        returns = df['Close'].pct_change().dropna()
        if len(returns) < 5:
            return 0.015
        
        # Use rolling standard deviation
        volatility = returns.rolling(window=min(10, len(returns))).std().iloc[-1]
        
        # Cap volatility at reasonable levels
        return min(max(volatility, 0.005), 0.05)  # Between 0.5% and 5%
    
    def calculate_bollinger_bands(self, df, window=20):
        """Calculate Bollinger Bands for realistic price ranges"""
        if len(df) < window or 'Close' not in df.columns:
            return None
        
        rolling_mean = df['Close'].rolling(window=window).mean()
        rolling_std = df['Close'].rolling(window=window).std()
        
        upper_band = rolling_mean + (2 * rolling_std)
        lower_band = rolling_mean - (2 * rolling_std)
        
        return {
            'upper': float(upper_band.iloc[-1]) if not pd.isna(upper_band.iloc[-1]) else None,
            'middle': float(rolling_mean.iloc[-1]) if not pd.isna(rolling_mean.iloc[-1]) else None,
            'lower': float(lower_band.iloc[-1]) if not pd.isna(lower_band.iloc[-1]) else None,
            'width_pct': float((upper_band.iloc[-1] - lower_band.iloc[-1]) / rolling_mean.iloc[-1] * 100) if not pd.isna(rolling_mean.iloc[-1]) else None
        }
    
    def get_support_resistance_levels(self, df):
        """Identify key support and resistance levels"""
        if len(df) < 20:
            return {'current': 0}
        
        # Ensure required columns exist
        required_cols = ['Close', 'High', 'Low']
        for col in required_cols:
            if col not in df.columns:
                return {'current': float(df['Close'].iloc[-1]) if 'Close' in df.columns else 0}
        
        # Simple approach: recent highs and lows
        recent_high = df['High'].tail(20).max()
        recent_low = df['Low'].tail(20).min()
        current = df['Close'].iloc[-1]
        
        # Psychological levels (round numbers)
        def find_psychological_levels(price):
            levels = []
            # Untuk harga IDR, round to nearest 50, 100
            base_100 = round(price / 100) * 100
            base_50 = round(price / 50) * 50
            
            levels.extend([
                base_100 - 200, base_100 - 100, base_100, base_100 + 100, base_100 + 200,
                base_50 - 100, base_50 - 50, base_50, base_50 + 50, base_50 + 100
            ])
            
            # Filter positive and unique levels
            unique_levels = sorted(list(set([l for l in levels if l > 0])))
            
            # Return levels near current price
            near_levels = [l for l in unique_levels if abs(l - current) / current < 0.1]  # Within 10%
            return near_levels[:5]  # Return top 5 nearest
        
        psych_levels = find_psychological_levels(current)
        
        return {
            'recent_high': float(recent_high),
            'recent_low': float(recent_low),
            'current': float(current),
            'psychological_levels': psych_levels
        }
    
    def predict_with_volatility_model(self, df, ticker=None, days=5):
        """Predict using volatility-based random walk with mean reversion"""
        try:
            # Get current price - prioritize real-time if ticker provided
            current_price = None
            
            if ticker and YFINANCE_AVAILABLE:
                current_price = self.get_realtime_price(ticker)
                
                # Update dataframe with latest data
                if current_price and not df.empty:
                    df = self.update_dataframe_with_realtime(df, ticker)
            
            # Fallback to dataframe if real-time not available
            if current_price is None or np.isnan(current_price):
                if df.empty or 'Close' not in df.columns:
                    return self._get_ultra_conservative_prediction(df, current_price)
                current_price = df['Close'].iloc[-1]
            
            # If dataframe is too small, use ultra conservative method
            if len(df) < 30:
                result = self._get_ultra_conservative_prediction(df, current_price)
                # Ensure current price is updated
                result['current_price'] = round(float(current_price), 2)
                return result
            
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
                if bb and bb['middle']:
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
                if 'recent_high' in sr_levels and sr_levels['recent_high'] and next_price > sr_levels['recent_high'] * 1.02:
                    next_price = sr_levels['recent_high'] * 0.98  # Resistance bounce
                
                if 'recent_low' in sr_levels and sr_levels['recent_low'] and next_price < sr_levels['recent_low'] * 0.98:
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
            
            # Format untuk display IDR
            def format_idr(price):
                return f"Rp {price:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.')
            
            return {
                'current_price': round(float(current_price), 2),
                'current_price_formatted': format_idr(current_price),
                'predictions': [round(float(p), 2) for p in predictions],
                'predictions_formatted': [format_idr(p) for p in predictions],
                'next_day_prediction': round(float(predictions[0]), 2),
                'next_day_prediction_formatted': format_idr(predictions[0]),
                'trend': trend,
                'confidence': round(float(confidence), 1),
                'potential_change_pct': round(((predictions[0] - current_price) / current_price * 100), 2),
                'avg_prediction': round(float(avg_prediction), 2),
                'avg_prediction_formatted': format_idr(avg_prediction),
                'volatility_pct': round(volatility * 100, 2),
                'bollinger_bands': bb,
                'support_resistance': sr_levels,
                'realistic_range': {
                    'optimistic': round(current_price * 1.05, 2),
                    'optimistic_formatted': format_idr(current_price * 1.05),
                    'pessimistic': round(current_price * 0.95, 2),
                    'pessimistic_formatted': format_idr(current_price * 0.95),
                    'most_likely': round(np.median(predictions), 2),
                    'most_likely_formatted': format_idr(np.median(predictions))
                },
                'data_source': 'Real-time Yahoo Finance' if ticker and current_price else 'Historical Data',
                'disclaimer': "Prediksi didasarkan pada volatilitas historis dan data real-time. Harga saham dapat berfluktuasi. Prediksi ini bukan rekomendasi investasi. Selalu lakukan analisis sendiri dan konsultasi dengan penasihat keuangan."
            }
            
        except Exception as e:
            print(f"Error in prediction: {e}")
            return self._get_ultra_conservative_prediction(df, None)
    
    def _get_ultra_conservative_prediction(self, df, current_price=None):
        """Ultra conservative prediction when data is limited"""
        try:
            if current_price is None:
                if df.empty or 'Close' not in df.columns:
                    current_price = 0
                else:
                    current_price = df['Close'].iloc[-1]
            
            # Simple mean reversion prediction
            next_price = current_price
            trend = "sideways"
            
            if not df.empty and len(df) >= 5 and 'Close' in df.columns:
                ma_5 = df['Close'].rolling(5).mean().iloc[-1]
                if not pd.isna(ma_5):
                    # Very small mean reversion
                    if current_price > ma_5 * 1.02:
                        next_price = current_price * 0.995  # Slight correction
                        trend = "slight correction"
                    elif current_price < ma_5 * 0.98:
                        next_price = current_price * 1.005  # Slight rebound
                        trend = "slight rebound"
            
            predictions = [next_price] * 5
            
            # Format untuk display IDR
            def format_idr(price):
                return f"Rp {price:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.')
            
            return {
                'current_price': round(float(current_price), 2),
                'current_price_formatted': format_idr(current_price),
                'predictions': [round(float(p), 2) for p in predictions],
                'predictions_formatted': [format_idr(p) for p in predictions],
                'next_day_prediction': round(float(next_price), 2),
                'next_day_prediction_formatted': format_idr(next_price),
                'trend': trend,
                'confidence': 40,  # Low confidence due to limited data
                'potential_change_pct': 0.0,
                'avg_prediction': round(float(current_price), 2),
                'avg_prediction_formatted': format_idr(current_price),
                'volatility_pct': 1.5,
                'bollinger_bands': None,
                'support_resistance': {'current': current_price},
                'realistic_range': {
                    'optimistic': round(current_price * 1.03, 2),
                    'optimistic_formatted': format_idr(current_price * 1.03),
                    'pessimistic': round(current_price * 0.97, 2),
                    'pessimistic_formatted': format_idr(current_price * 0.97),
                    'most_likely': round(current_price, 2),
                    'most_likely_formatted': format_idr(current_price)
                },
                'data_source': 'Limited Historical Data',
                'disclaimer': "Prediksi sangat konservatif karena data terbatas. Harga real-time mungkin tidak tersedia. Tidak direkomendasikan untuk keputusan investasi."
            }
            
        except Exception as e:
            print(f"Error in ultra conservative prediction: {e}")
            # Return minimal response
            return {
                'current_price': 0,
                'current_price_formatted': 'Rp 0',
                'predictions': [0] * 5,
                'predictions_formatted': ['Rp 0'] * 5,
                'next_day_prediction': 0,
                'next_day_prediction_formatted': 'Rp 0',
                'trend': 'unknown',
                'confidence': 10,
                'potential_change_pct': 0,
                'avg_prediction': 0,
                'avg_prediction_formatted': 'Rp 0',
                'volatility_pct': 0,
                'bollinger_bands': None,
                'support_resistance': {'current': 0},
                'realistic_range': {
                    'optimistic': 0,
                    'optimistic_formatted': 'Rp 0',
                    'pessimistic': 0,
                    'pessimistic_formatted': 'Rp 0',
                    'most_likely': 0,
                    'most_likely_formatted': 'Rp 0'
                },
                'data_source': 'Error',
                'disclaimer': "Terjadi error dalam prediksi. Silakan coba lagi atau periksa koneksi internet."
            }
    
    def generate_trading_scenarios(self, df, ticker=None):
        """Generate realistic trading scenarios instead of precise predictions"""
        try:
            # Get current price
            current_price = None
            if ticker and YFINANCE_AVAILABLE:
                current_price = self.get_realtime_price(ticker)
            
            if current_price is None or np.isnan(current_price):
                if df.empty or 'Close' not in df.columns:
                    return self._get_basic_scenarios(df, current_price)
                current_price = df['Close'].iloc[-1]
            
            if len(df) < 20:
                return self._get_basic_scenarios(df, current_price)
            
            volatility = self.calculate_historical_volatility(df)
            
            # Format untuk display IDR
            def format_idr(price):
                return f"Rp {price:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.')
            
            scenarios = {
                'bullish_scenario': {
                    'probability': '30%',
                    'description': 'Breakout atas dengan volume tinggi',
                    'target': round(current_price * (1 + volatility * 3), 2),
                    'target_formatted': format_idr(current_price * (1 + volatility * 3)),
                    'stop_loss': round(current_price * (1 - volatility * 2), 2),
                    'stop_loss_formatted': format_idr(current_price * (1 - volatility * 2)),
                    'condition': 'Volume > rata-rata 20 hari',
                    'risk': 'Medium-High'
                },
                'bearish_scenario': {
                    'probability': '25%',
                    'description': 'Koreksi menuju support',
                    'target': round(current_price * (1 - volatility * 2.5), 2),
                    'target_formatted': format_idr(current_price * (1 - volatility * 2.5)),
                    'stop_loss': round(current_price * (1 + volatility * 1.5), 2),
                    'stop_loss_formatted': format_idr(current_price * (1 + volatility * 1.5)),
                    'condition': 'RSI > 70 dan MACD negatif',
                    'risk': 'Medium'
                },
                'sideways_scenario': {
                    'probability': '45%',
                    'description': 'Konsolidasi dalam range',
                    'range': {
                        'upper': round(current_price * (1 + volatility * 1.5), 2),
                        'upper_formatted': format_idr(current_price * (1 + volatility * 1.5)),
                        'lower': round(current_price * (1 - volatility * 1.5), 2),
                        'lower_formatted': format_idr(current_price * (1 - volatility * 1.5))
                    },
                    'strategy': 'Range trading',
                    'risk': 'Low'
                }
            }
            
            return scenarios
            
        except Exception as e:
            print(f"Error generating scenarios: {e}")
            return self._get_basic_scenarios(df, None)
    
    def _get_basic_scenarios(self, df, current_price=None):
        """Basic scenarios when data is limited"""
        if current_price is None:
            if df.empty or 'Close' not in df.columns:
                current_price = 0
            else:
                current_price = df['Close'].iloc[-1]
        
        return {
            'conservative_advice': {
                'message': 'Data tidak cukup untuk analisis teknis mendalam',
                'recommendation': 'Tunggu konfirmasi lebih lanjut',
                'suggested_action': 'Monitor dan tunggu setup yang jelas',
                'risk_level': 'High (karena ketidakpastian)',
                'current_price': round(float(current_price), 2),
                'current_price_formatted': f"Rp {current_price:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.')
            }
        }


# Untuk backward compatibility dengan kode yang mengimpor PricePredictor
PricePredictor = ConservativePricePredictor
