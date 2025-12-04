import pickle
import os
import time
import hashlib
from datetime import datetime, timedelta

class DataCache:
    def __init__(self, cache_dir="cache", ttl_hours=24):
        self.cache_dir = cache_dir
        self.ttl_seconds = ttl_hours * 3600
        
        # Create cache directory if not exists
        if not os.path.exists(cache_dir):
            os.makedirs(cache_dir)
    
    def _get_cache_key(self, ticker, data_type):
        """Generate unique cache key"""
        key_str = f"{ticker}_{data_type}"
        return hashlib.md5(key_str.encode()).hexdigest()
    
    def _get_cache_path(self, ticker, data_type):
        """Get cache file path"""
        key = self._get_cache_key(ticker, data_type)
        return os.path.join(self.cache_dir, f"{key}.pkl")
    
    def get(self, ticker, data_type):
        """Get data from cache if exists and not expired"""
        cache_path = self._get_cache_path(ticker, data_type)
        
        if not os.path.exists(cache_path):
            return None
        
        try:
            with open(cache_path, 'rb') as f:
                cached_data = pickle.load(f)
            
            # Check if cache is expired
            cache_time = cached_data.get('timestamp', 0)
            current_time = time.time()
            
            if current_time - cache_time > self.ttl_seconds:
                os.remove(cache_path)  # Remove expired cache
                return None
            
            return cached_data['data']
        except:
            return None
    
    def set(self, ticker, data_type, data):
        """Save data to cache"""
        cache_path = self._get_cache_path(ticker, data_type)
        
        cache_data = {
            'timestamp': time.time(),
            'data': data
        }
        
        try:
            with open(cache_path, 'wb') as f:
                pickle.dump(cache_data, f)
            return True
        except:
            return False

# Global cache instance
cache = DataCache()
