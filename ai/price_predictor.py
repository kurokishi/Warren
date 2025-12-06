import pandas as pd
import numpy as np
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import StandardScaler
import warnings
warnings.filterwarnings('ignore')

class PricePredictor:
    """
    Simple ML-based price prediction for next 5 days
    """
    
    def __init__(self):
        self.model = LinearRegression()
        self.scaler = StandardScaler()
    
    def prepare_features(self, df, window=5):
        """Prepare features for prediction"""
        features = pd.DataFrame(index=df.index)
        
        # Price features
        features['close'] = df['Close']
        features['returns'] = df['Close'].pct_change()
        features['volume'] = df['Volume']
        
        # Rolling statistics
        features['ma_5'] = df['Close'].rolling(window=5).mean()
        features['ma_10'] = df['Close'].rolling(window=10).mean()
        features['volatility'] = df['Close'].rolling(window=10).std()
        
        # Momentum features
        features['momentum'] = df['Close'] - df['Close'].shift(5)
        
        # Drop NaN
        features = features.dropna()
        
        return features
    
    def predict_next_days(self, df, days=5):
        """Predict price for next 'days'"""
        try:
            if len(df) < 30:
                return self._get_default_prediction(df)
            
            # Prepare features
            features = self.prepare_features(df)
            
            if len(features) < 20:
                return self._get_default_prediction(df)
            
            # Create training data
            X = features[:-days].values
            y = features['close'].shift(-days).dropna().values
            
            if len(X) != len(y):
                min_len = min(len(X), len(y))
                X = X[:min_len]
                y = y[:min_len]
            
            # Scale features
            X_scaled = self.scaler.fit_transform(X)
            
            # Train model
            self.model.fit(X_scaled, y)
            
            # Predict next days
            last_features = features.iloc[-days:].values
            last_scaled = self.scaler.transform(last_features)
            
            predictions = self.model.predict(last_scaled)
            current_price = df['Close'].iloc[-1]
            
            # Calculate confidence
            confidence = self._calculate_confidence(predictions, current_price)
            
            # Determine trend
            trend = self._determine_trend(predictions)
            
            return {
                'current_price': round(float(current_price), 2),
                'predictions': [round(float(p), 2) for p in predictions],
                'next_day_prediction': round(float(predictions[0]), 2),
                'trend': trend,
                'confidence': round(float(confidence), 1),
                'potential_change_pct': round(((predictions[0] - current_price) / current_price * 100), 2),
                'avg_prediction': round(float(np.mean(predictions)), 2)
            }
            
        except Exception as e:
            return self._get_default_prediction(df)
    
    def _calculate_confidence(self, predictions, current_price):
        """Calculate prediction confidence based on variance"""
        if len(predictions) < 2:
            return 50
        
        variance = np.std(predictions) / current_price
        confidence = max(30, min(95, 100 - (variance * 500)))
        return confidence
    
    def _determine_trend(self, predictions):
        """Determine trend direction"""
        if len(predictions) < 2:
            return "neutral"
        
        first = predictions[0]
        last = predictions[-1]
        
        if last > first * 1.02:
            return "bullish"
        elif last < first * 0.98:
            return "bearish"
        else:
            return "neutral"
    
    def _get_default_prediction(self, df):
        """Get default prediction when ML fails"""
        current_price = df['Close'].iloc[-1] if len(df) > 0 else 0
        
        # Simple momentum-based prediction
        if len(df) >= 5:
            ma_5 = df['Close'].rolling(5).mean().iloc[-1]
            trend = "bullish" if current_price > ma_5 else "bearish" if current_price < ma_5 else "neutral"
            confidence = 50
        else:
            trend = "neutral"
            confidence = 30
        
        return {
            'current_price': round(float(current_price), 2),
            'predictions': [round(current_price * (1 + 0.01*i), 2) for i in range(5)],
            'next_day_prediction': round(float(current_price), 2),
            'trend': trend,
            'confidence': confidence,
            'potential_change_pct': 0.0,
            'avg_prediction': round(float(current_price), 2)
        }
