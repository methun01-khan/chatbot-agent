from textblob import TextBlob
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
import re

class SentimentAnalyzer:
    def __init__(self):
        self.vader = SentimentIntensityAnalyzer()
        print("✅ Sentiment Analyzer initialized!")
    
    def analyze_sentiment_vader(self, text):
        """Analyze sentiment using VADER (best for social media text)"""
        scores = self.vader.polarity_scores(text)
        
        # Determine overall sentiment
        if scores['compound'] >= 0.05:
            sentiment = 'positive'
        elif scores['compound'] <= -0.05:
            sentiment = 'negative'
        else:
            sentiment = 'neutral'
        
        return {
            'sentiment': sentiment,
            'compound': scores['compound'],
            'positive': scores['pos'],
            'neutral': scores['neu'],
            'negative': scores['neg'],
            'emoji': self.get_sentiment_emoji(sentiment)
        }
    
    def analyze_sentiment_textblob(self, text):
        """Analyze sentiment using TextBlob"""
        blob = TextBlob(text)
        polarity = blob.sentiment.polarity
        subjectivity = blob.sentiment.subjectivity
        
        if polarity > 0.1:
            sentiment = 'positive'
        elif polarity < -0.1:
            sentiment = 'negative'
        else:
            sentiment = 'neutral'
        
        return {
            'sentiment': sentiment,
            'polarity': polarity,
            'subjectivity': subjectivity
        }
    
    def get_sentiment_emoji(self, sentiment):
        """Get emoji for sentiment"""
        emojis = {
            'positive': '😊',
            'negative': '😞',
            'neutral': '😐'
        }
        return emojis.get(sentiment, '😐')
    
    def get_detailed_sentiment(self, text):
        """Combine both methods for detailed analysis"""
        vader_result = self.analyze_sentiment_vader(text)
        textblob_result = self.analyze_sentiment_textblob(text)
        
        return {
            'vader': vader_result,
            'textblob': textblob_result,
            'overall_sentiment': vader_result['sentiment'],
            'confidence': abs(vader_result['compound'])
        }
    
    def generate_sentiment_response(self, sentiment_data):
        """Generate appropriate response based on sentiment"""
        sentiment = sentiment_data['vader']['sentiment']
        compound = sentiment_data['vader']['compound']
        
        if sentiment == 'positive':
            if compound > 0.5:
                return "I'm glad you're feeling great! 😊"
            else:
                return "That sounds positive! 🙂"
        elif sentiment == 'negative':
            if compound < -0.5:
                return "I sense you might be upset. I'm here to help. 💙"
            else:
                return "I understand. How can I assist you? 🤝"
        else:
            return "I'm listening. Tell me more."