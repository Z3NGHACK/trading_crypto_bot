import os
import pandas as pd
import requests
try:
    from textblob import TextBlob
    TEXTBLOB_AVAILABLE = True
except ImportError:
    TEXTBLOB_AVAILABLE = False
    print("Warning: textblob not installed. Sentiment analysis will be disabled. Install with 'pip install textblob'.")

class SentimentAnalyzer:
    def __init__(self, asset_name='BTC', news_api_key=None):
        self.asset_name = asset_name
        self.news_api_key = news_api_key or os.getenv('NEWS_API_KEY')
    
    def fetch_news(self):
        """Fetch news articles using NewsAPI or web search"""
        if not self.news_api_key:
            print("Warning: No NEWS_API_KEY provided. Using placeholder data.")
            return []  # Placeholder
        try:
            url = f"https://newsapi.org/v2/everything?q={self.asset_name}+cryptocurrency&apiKey={self.news_api_key}"
            response = requests.get(url)
            response.raise_for_status()
            articles = response.json().get('articles', [])
            return [article['title'] + ' ' + article.get('description', '') for article in articles[:10]]
        except Exception as e:
            print(f"Error fetching news: {e}")
            return []
    
    def analyze_news_sentiment(self, news_texts=None):
        if not TEXTBLOB_AVAILABLE:
            return 'neutral', 0
        news_texts = news_texts or self.fetch_news()
        if not news_texts:
            return 'neutral', 0
        try:
            sentiments = [TextBlob(text).sentiment.polarity for text in news_texts]
            avg_sentiment = sum(sentiments) / len(sentiments) if sentiments else 0
            if avg_sentiment > 0.2:
                return 'bullish', avg_sentiment
            elif avg_sentiment < -0.2:
                return 'bearish', abs(avg_sentiment)
            return 'neutral', 0
        except Exception as e:
            print(f"Error in sentiment analysis: {e}")
            return 'neutral', 0
    
    def get_social_sentiment(self, tweets):
        return self.analyze_news_sentiment(tweets)
    
    def predict_impact(self, technical_signal, sentiment):
        if sentiment[0] == 'neutral':
            return technical_signal, 0.5
        if technical_signal == 'buy' and sentiment[0] == 'bullish':
            return 'strong_buy', 0.8
        elif technical_signal == 'sell' and sentiment[0] == 'bearish':
            return 'strong_sell', 0.8
        return technical_signal, 0.5