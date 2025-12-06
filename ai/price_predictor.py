import pandas as pd
import numpy as np
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import StandardScaler
import warnings
import yfinance as yf
from datetime import datetime, timedelta
import time

warnings.filterwarnings('ignore')

class ConservativePricePredictor:
    """
    CONSERVATIVE price prediction based on historical volatility
    - Maximum daily change: ±3% (realistic for blue chips)
    - Uses Bollinger Bands for realistic range
    - Emphasizes mean reversion
    - Clear disclaimer about limitations
    - Real-time data fetching capability
    """
    
    def __init__(self):
        self.model = LinearRegression()
        self.scaler = StandardScaler()
        
        # Conservative parameters for Indonesian blue chips
        self.MAX_DAILY_CHANGE = 0.03  # Max 3% daily change (realistic)
        self.VOLATILITY_WINDOW = 20   # Lookback for volatility calculation
        self.CONFIDENCE_DECAY = 0.8   # Confidence decays over prediction horizon
        
        # Cache untuk data per ticker
        self.data_cache = {}
        self.price_cache = {}
        self.cache_timeout = 60  # Cache timeout 60 detik
    
    # ========== CACHE MANAGEMENT ==========
    
    def clear_cache(self, ticker: str = None):
        """Clear cache untuk ticker tertentu atau semua cache"""
        if ticker:
            cache_keys = [k for k in self.data_cache.keys() if k.startswith(ticker)]
            for key in cache_keys:
                self.data_cache.pop(key, None)
                self.price_cache.pop(key, None)
            print(f"Cache cleared for {ticker}")
        else:
            self.data_cache = {}
            self.price_cache = {}
            print("All cache cleared")
    
    # ========== MAIN PREDICTION METHOD ==========
    
    def predict_for_ticker(self, ticker: str, days: int = 5, use_cache: bool = True) -> dict:
        """
        Main method untuk prediksi berdasarkan ticker
        
        Args:
            ticker: Stock ticker (e.g., 'TLKM.JK')
            days: Number of days to predict
            use_cache: Whether to use cached data
            
        Returns:
            Dictionary dengan hasil prediksi
        """
        start_time = time.time()
        
        try:
            # Validasi input
            if not ticker or not isinstance(ticker, str):
                return self._create_error_response("Ticker tidak valid")
            
            ticker = ticker.strip().upper()
            if not ticker:
                return self._create_error_response("Ticker tidak boleh kosong")
            
            print(f"🔍 Predicting for {ticker} for {days} days...")
            
            # Format ticker untuk Yahoo Finance
            ticker_yf = self._format_ticker_for_yahoo(ticker)
            
            # Cek cache
            cache_key = f"{ticker}_{days}"
            if use_cache and cache_key in self.data_cache:
                cached_data = self.data_cache[cache_key]
                cache_age = time.time() - cached_data['timestamp']
                
                if cache_age < self.cache_timeout:
                    print(f"⚡ Using cached prediction (age: {cache_age:.1f}s)")
                    result = cached_data['result'].copy()
                    result['cache_used'] = True
                    result['cache_age_seconds'] = cache_age
                    return result
            
            # Step 1: Dapatkan data historis
            df = self._get_fresh_historical_data(ticker_yf)
            
            if df.empty:
                return self._create_error_response(
                    f"Tidak dapat mengambil data untuk {ticker}. "
                    f"Pastikan ticker benar (contoh: TLKM.JK, BBCA.JK)"
                )
            
            # Step 2: Dapatkan harga saat ini
            current_price = self._get_current_price(ticker_yf, df)
            
            if current_price <= 0:
                return self._create_error_response(
                    f"Tidak dapat mendapatkan harga untuk {ticker}. "
                    f"Mungkin ticker tidak valid atau data tidak tersedia."
                )
            
            # Step 3: Generate prediction dengan harga yang sudah didapat
            result = self.predict_with_volatility_model_and_price(df, current_price, days)
            
            # Step 4: Tambahkan metadata
            result.update({
                'ticker': ticker,
                'data_points': len(df),
                'latest_data_date': df.index[-1].strftime('%Y-%m-%d') if len(df) > 0 else 'N/A',
                'price_source': self._get_price_source(ticker_yf, df),
                'realtime_price_used': self._is_realtime_price_used(ticker_yf, df),
                'cache_used': False,
                'processing_time': round(time.time() - start_time, 2),
                'error': False
            })
            
            # Step 5: Cache result jika diaktifkan
            if use_cache:
                self.data_cache[cache_key] = {
                    'result': result,
                    'timestamp': time.time()
                }
                print(f"💾 Result cached with key: {cache_key}")
            
            print(f"✅ Prediction complete for {ticker}")
            return result
            
        except Exception as e:
            print(f"❌ Error in predict_for_ticker: {e}")
            return self._create_error_response(f"Internal error: {str(e)}", ticker)
    
    def _create_error_response(self, message: str, ticker: str = "") -> dict:
        """Create standardized error response"""
        return {
            'error': True,
            'message': message,
            'ticker': ticker,
            'current_price': 0,
            'predictions': [],
            'next_day_prediction': 0,
            'trend': 'unknown',
            'trend_icon': '❓',
            'trend_percentage': 0.0,
            'confidence': 0,
            'potential_change_pct': 0.0,
            'avg_prediction': 0,
            'volatility_pct': 0.0,
            'bollinger_bands': None,
            'support_resistance': {},
            'realistic_range': {
                'optimistic': 0,
                'pessimistic': 0,
                'most_likely': 0
            },
            'disclaimer': "Error dalam prediksi. Silakan coba lagi.",
            'processing_time': 0
        }
    
    # ========== HELPER METHODS ==========
    
    def _format_ticker_for_yahoo(self, ticker: str) -> str:
        """Format ticker untuk Yahoo Finance"""
        ticker = ticker.strip().upper()
        
        # Jika ticker tidak mengandung .JK, tambahkan
        if not ticker.endswith('.JK'):
            return f"{ticker}.JK"
        
        return ticker
    
    def _get_fresh_historical_data(self, ticker: str) -> pd.DataFrame:
        """Get fresh historical data from Yahoo Finance"""
        try:
            print(f"📥 Fetching data for {ticker}...")
            stock = yf.Ticker(ticker)
            
            # Coba beberapa period untuk memastikan dapat data
            periods = ["3mo", "1mo", "6mo", "1y"]
            
            for period in periods:
                df = stock.history(period=period)
                if not df.empty and len(df) >= 5:
                    print(f"✅ Got {len(df)} data points for {ticker}")
                    return df
            
            # Jika semua period gagal, coba dengan date range
            end_date = datetime.now()
            start_date = end_date - timedelta(days=90)
            df = stock.history(start=start_date, end=end_date)
            
            if df.empty:
                print(f"❌ No data found for {ticker}")
                return pd.DataFrame()
            
            return df
            
        except Exception as e:
            print(f"❌ Error fetching data for {ticker}: {e}")
            return pd.DataFrame()
    
    def _get_current_price(self, ticker: str, df: pd.DataFrame) -> float:
        """Get current price from multiple sources"""
        try:
            # Cek cache harga dulu
            if ticker in self.price_cache:
                cached_time, cached_price = self.price_cache[ticker]
                if time.time() - cached_time < 30:  # Cache 30 detik untuk harga
                    print(f"📊 Using cached price for {ticker}: {cached_price}")
                    return cached_price
            
            stock = yf.Ticker(ticker)
            
            # Method 1: Try to get real-time price
            try:
                info = stock.info
                price_keys = ['currentPrice', 'regularMarketPrice', 'previousClose', 
                            'ask', 'bid', 'open']
                
                for key in price_keys:
                    price = info.get(key)
                    if price and not np.isnan(price):
                        print(f"✅ Got real-time price for {ticker}: {price} (from {key})")
                        # Cache the price
                        self.price_cache[ticker] = (time.time(), float(price))
                        return float(price)
            except:
                pass
            
            # Method 2: Try to get latest from 1-day history
            try:
                hist = stock.history(period="1d")
                if not hist.empty:
                    price = hist['Close'].iloc[-1]
                    print(f"✅ Got 1-day price for {ticker}: {price}")
                    self.price_cache[ticker] = (time.time(), float(price))
                    return float(price)
            except:
                pass
            
            # Method 3: Use last close from the dataframe
            if len(df) > 0:
                price = df['Close'].iloc[-1]
                print(f"⚠️ Using last close price for {ticker}: {price}")
                return float(price)
            
            print(f"❌ Could not get price for {ticker}")
            return 0.0
            
        except Exception as e:
            print(f"❌ Error getting price for {ticker}: {e}")
            if len(df) > 0:
                return float(df['Close'].iloc[-1])
            return 0.0
    
    def _get_price_source(self, ticker: str, df: pd.DataFrame) -> str:
        """Determine the source of the price"""
        try:
            stock = yf.Ticker(ticker)
            info = stock.info
            
            if info.get('currentPrice') and not np.isnan(info.get('currentPrice')):
                return "real-time (currentPrice)"
            elif info.get('regularMarketPrice') and not np.isnan(info.get('regularMarketPrice')):
                return "real-time (regularMarketPrice)"
            else:
                return "historical (last close)"
        except:
            return "historical (last close)"
    
    def _is_realtime_price_used(self, ticker: str, df: pd.DataFrame) -> bool:
        """Check if real-time price was used"""
        try:
            stock = yf.Ticker(ticker)
            info = stock.info
            
            if (info.get('currentPrice') and not np.isnan(info.get('currentPrice'))) or \
               (info.get('regularMarketPrice') and not np.isnan(info.get('regularMarketPrice'))):
                return True
            return False
        except:
            return False
    
    # ========== PREDICTION ENGINE ==========
    
    def predict_with_volatility_model_and_price(self, df: pd.DataFrame, current_price: float, days: int = 5) -> dict:
        """
        Modified version of predict_with_volatility_model that accepts current_price parameter
        """
        if len(df) < 10:
            return self._get_ultra_conservative_prediction_with_price(df, current_price)
        
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
            mean_reversion_factor = 0
            if bb and bb.get('middle'):
                mean_reversion_factor = 0.3 * (bb['middle'] - last_price) / bb['middle']
            
            # Random component based on historical volatility
            random_component = np.random.normal(0, volatility) * 0.7
            
            # Combined daily change (capped)
            daily_change = mean_reversion_factor + random_component
            daily_change = max(-self.MAX_DAILY_CHANGE, min(self.MAX_DAILY_CHANGE, daily_change))
            
            next_price = last_price * (1 + daily_change)
            
            # Apply support/resistance boundaries
            if sr_levels.get('recent_high') and next_price > sr_levels['recent_high'] * 1.02:
                next_price = sr_levels['recent_high'] * 0.98
            
            if sr_levels.get('recent_low') and next_price < sr_levels['recent_low'] * 0.98:
                next_price = sr_levels['recent_low'] * 1.02
            
            predictions.append(next_price)
            last_price = next_price
        
        # Calculate trend
        avg_prediction = np.mean(predictions)
        trend_percentage = (avg_prediction - current_price) / current_price * 100
        
        # Determine trend
        if abs(trend_percentage) < 0.5:
            trend = "sideways"
            trend_icon = "➡️"
        elif trend_percentage > 2.0:
            trend = "bullish"
            trend_icon = "📈"
        elif trend_percentage > 0:
            trend = "slightly bullish"
            trend_icon = "↗️"
        elif trend_percentage < -2.0:
            trend = "bearish"
            trend_icon = "📉"
        else:
            trend = "slightly bearish"
            trend_icon = "↘️"
        
        # Confidence decays with prediction horizon
        confidence = max(30, 70 * (self.CONFIDENCE_DECAY ** (days-1)))
        
        # Calculate realistic range based on volatility
        volatility_multiplier = min(days * 0.015, 0.05)
        optimistic = current_price * (1 + volatility_multiplier)
        pessimistic = current_price * (1 - volatility_multiplier)
        
        # Calculate potential change for next day
        potential_change_pct = ((predictions[0] - current_price) / current_price * 100) if predictions else 0
        
        return {
            'current_price': round(float(current_price), 2),
            'predictions': [round(float(p), 2) for p in predictions],
            'next_day_prediction': round(float(predictions[0]), 2) if predictions else round(float(current_price), 2),
            'trend': trend,
            'trend_icon': trend_icon,
            'trend_percentage': round(float(trend_percentage), 2),
            'confidence': round(float(confidence), 1),
            'potential_change_pct': round(float(potential_change_pct), 2),
            'avg_prediction': round(float(avg_prediction), 2),
            'volatility_pct': round(volatility * 100, 2),
            'bollinger_bands': bb,
            'support_resistance': sr_levels,
            'realistic_range': {
                'optimistic': round(float(optimistic), 2),
                'pessimistic': round(float(pessimistic), 2),
                'most_likely': round(np.median(predictions), 2) if predictions else round(float(current_price), 2)
            },
            'disclaimer': "Prediksi didasarkan pada volatilitas historis. Pergerakan aktual bisa berbeda. Gunakan hanya sebagai referensi tambahan."
        }
    
    def _get_ultra_conservative_prediction_with_price(self, df: pd.DataFrame, current_price: float) -> dict:
        """Ultra conservative prediction when data is limited with custom price"""
        # Simple mean reversion prediction
        if len(df) >= 5:
            ma_5 = df['Close'].rolling(5).mean().iloc[-1]
            # Very small mean reversion
            if current_price > ma_5 * 1.02:
                next_price = current_price * 0.995  # Slight correction
                trend = "slight correction"
                trend_icon = "↘️"
                trend_percentage = -0.5
            elif current_price < ma_5 * 0.98:
                next_price = current_price * 1.005  # Slight rebound
                trend = "slight rebound"
                trend_icon = "↗️"
                trend_percentage = 0.5
            else:
                next_price = current_price
                trend = "sideways"
                trend_icon = "➡️"
                trend_percentage = 0.0
        else:
            next_price = current_price
            trend = "sideways"
            trend_icon = "➡️"
            trend_percentage = 0.0
        
        predictions = [next_price] * 5
        
        return {
            'current_price': round(float(current_price), 2),
            'predictions': [round(float(p), 2) for p in predictions],
            'next_day_prediction': round(float(next_price), 2),
            'trend': trend,
            'trend_icon': trend_icon,
            'trend_percentage': round(float(trend_percentage), 2),
            'confidence': 40.0,
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
    
    # ========== ORIGINAL METHODS (KEPT FOR BACKWARD COMPATIBILITY) ==========
    
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
        return min(max(volatility, 0.005), 0.05)
    
    def calculate_bollinger_bands(self, df, window=20):
        """Calculate Bollinger Bands for realistic price ranges"""
        if len(df) < window:
            return None
        
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
            return {'current': df['Close'].iloc[-1] if len(df) > 0 else 0}
        
        recent_high = df['High'].tail(20).max()
        recent_low = df['Low'].tail(20).min()
        current = df['Close'].iloc[-1]
        
        def find_psychological_levels(price):
            levels = []
            base = round(price / 100) * 100
            levels.extend([base - 200, base - 100, base, base + 100, base + 200])
            return [l for l in levels if l > 0]
        
        psych_levels = find_psychological_levels(current)
        
        return {
            'recent_high': float(recent_high),
            'recent_low': float(recent_low),
            'current': float(current),
            'psychological_levels': psych_levels[:3]
        }
    
    def predict_with_volatility_model(self, df, days=5):
        """
        Original method - kept for backward compatibility
        Uses last price from dataframe
        """
        if len(df) == 0:
            return self._get_ultra_conservative_prediction_with_price(df, 0)
        
        current_price = df['Close'].iloc[-1]
        return self.predict_with_volatility_model_and_price(df, current_price, days)
    
    def _get_ultra_conservative_prediction(self, df):
        """Original ultra conservative prediction method"""
        if len(df) == 0:
            current_price = 0
        else:
            current_price = df['Close'].iloc[-1]
        
        return self._get_ultra_conservative_prediction_with_price(df, current_price)
    
    def generate_trading_scenarios(self, df):
        """Generate realistic trading scenarios instead of precise predictions"""
        if len(df) < 20:
            return self._get_basic_scenarios(df)
        
        current_price = df['Close'].iloc[-1]
        volatility = self.calculate_historical_volatility(df)
        
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

# Alias untuk compatibility
PricePredictor = ConservativePricePredictor
