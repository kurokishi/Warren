import requests
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
import re
import pandas as pd
from typing import List, Dict
import time

class NewsSentimentAnalyzer:
    """
    News sentiment analysis for Indonesian stocks
    """
    
    def __init__(self):
        self.sources = {
            'kontan': 'https://investasi.kontan.co.id/search',
            'idxchannel': 'https://www.idxchannel.com/search',
            'investing': 'https://www.investing.com/equities/'
        }
        
        self.sentiment_keywords = {
            'positive': ['naik', 'menguat', 'melonjak', 'untung', 'laba', 'dividen', 'buyback', 
                        'rekomendasi beli', 'prospek cerah', 'growth', 'positif'],
            'negative': ['turun', 'melemah', 'anjlok', 'rugi', 'resiko', 'jual', 'koreksi',
                        'peringatan', 'masalah', 'negatif', 'bearish'],
            'neutral': ['stabil', 'fluktuatif', 'sideways', 'konsolidasi']
        }
    
    def fetch_news(self, ticker: str, days_back: int = 7) -> List[Dict]:
        """Fetch recent news for a ticker"""
        news_items = []
        
        # Format ticker untuk search
        search_ticker = ticker.replace('.JK', '')
        
        # Simulasi data news (dalam implementasi real, akan scraping website)
        # Untuk MVP, kita gunakan mock data dulu
        mock_news = self._get_mock_news(search_ticker)
        
        # Filter by date
        cutoff_date = datetime.now() - timedelta(days=days_back)
        
        for news in mock_news:
            news_date = datetime.strptime(news['date'], '%Y-%m-%d')
            if news_date >= cutoff_date:
                news_items.append(news)
        
        return news_items[:10]  # Limit to 10 items
    
    def analyze_sentiment(self, text: str) -> Dict:
        """Analyze sentiment of news text"""
        text_lower = text.lower()
        
        positive_score = sum(1 for word in self.sentiment_keywords['positive'] 
                           if word in text_lower)
        negative_score = sum(1 for word in self.sentiment_keywords['negative'] 
                           if word in text_lower)
        
        total_score = positive_score + negative_score
        
        if total_score == 0:
            sentiment = 'neutral'
            score = 0
        elif positive_score > negative_score:
            sentiment = 'positive'
            score = positive_score / total_score
        elif negative_score > positive_score:
            sentiment = 'negative'
            score = -negative_score / total_score
        else:
            sentiment = 'neutral'
            score = 0
        
        return {
            'sentiment': sentiment,
            'score': round(score, 2),
            'positive_keywords': positive_score,
            'negative_keywords': negative_score
        }
    
    def get_news_summary(self, ticker: str) -> Dict:
        """Get comprehensive news analysis for a ticker"""
        news_items = self.fetch_news(ticker)
        
        if not news_items:
            return {
                'total_news': 0,
                'sentiment': 'neutral',
                'avg_score': 0,
                'latest_news': [],
                'recommendation': 'Tidak ada berita terkini'
            }
        
        # Analyze each news
        analyzed_news = []
        scores = []
        
        for news in news_items:
            sentiment = self.analyze_sentiment(news['title'] + ' ' + news.get('summary', ''))
            analyzed_news.append({
                'title': news['title'],
                'date': news['date'],
                'sentiment': sentiment['sentiment'],
                'score': sentiment['score'],
                'source': news.get('source', 'kontan')
            })
            scores.append(sentiment['score'])
        
        # Calculate overall sentiment
        avg_score = sum(scores) / len(scores) if scores else 0
        
        if avg_score > 0.1:
            overall_sentiment = 'positive'
            recommendation = 'Sentimen berita positif'
        elif avg_score < -0.1:
            overall_sentiment = 'negative'
            recommendation = 'Sentimen berita negatif'
        else:
            overall_sentiment = 'neutral'
            recommendation = 'Sentimen berita netral'
        
        return {
            'total_news': len(analyzed_news),
            'sentiment': overall_sentiment,
            'avg_score': round(avg_score, 2),
            'latest_news': analyzed_news[:5],  # Latest 5 news
            'recommendation': recommendation,
            'positive_count': sum(1 for n in analyzed_news if n['sentiment'] == 'positive'),
            'negative_count': sum(1 for n in analyzed_news if n['sentiment'] == 'negative'),
            'neutral_count': sum(1 for n in analyzed_news if n['sentiment'] == 'neutral')
        }
    
    def _get_mock_news(self, ticker: str) -> List[Dict]:
        """Mock news data for demonstration"""
        news_templates = [
            {
                'title': f'{ticker} Menunjukkan Kinerja Kuartal yang Kuat',
                'summary': f'Emiten {ticker} melaporkan peningkatan laba bersih sebesar 15% pada kuartal terakhir.',
                'date': (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d'),
                'source': 'kontan'
            },
            {
                'title': f'Analis Merekomendasikan Beli untuk {ticker}',
                'summary': f'Beberapa analis sekuritas memberikan rekomendasi beli untuk saham {ticker} dengan target harga yang menarik.',
                'date': (datetime.now() - timedelta(days=2)).strftime('%Y-%m-%d'),
                'source': 'idxchannel'
            },
            {
                'title': f'{ticker} Bagikan Dividen Tunai',
                'summary': f'Perusahaan mengumumkan pembagian dividen tunai sebesar Rp 100 per saham.',
                'date': (datetime.now() - timedelta(days=3)).strftime('%Y-%m-%d'),
                'source': 'kontan'
            },
            {
                'title': f'Harga {ticker} Terkoreksi 2%',
                'summary': f'Saham {ticker} mengalami koreksi setelah mencapai level resistance.',
                'date': (datetime.now() - timedelta(days=4)).strftime('%Y-%m-%d'),
                'source': 'investing'
            },
            {
                'title': f'{ticker} Ekspansi ke Pasar Baru',
                'summary': f'Perusahaan berencana melakukan ekspansi bisnis ke pasar Asia Tenggara.',
                'date': (datetime.now() - timedelta(days=5)).strftime('%Y-%m-%d'),
                'source': 'kontan'
            }
        ]
        
        return news_templates
