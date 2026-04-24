import requests
from config import API_KEYS, DEFAULT_LOCATION
from datetime import datetime

class ExternalAPIs:
    def __init__(self):
        self.weather_key = API_KEYS.get('openweathermap', '')
        self.news_key = API_KEYS.get('newsapi', '')
        print("✅ External APIs initialized!")
    
    def get_weather(self, city=None):
        """Get weather information"""
        if not self.weather_key or self.weather_key == 'YOUR_OPENWEATHERMAP_API_KEY':
            return {
                'error': True,
                'message': 'Weather API key not configured. Please add your OpenWeatherMap API key in config.py'
            }
        
        city = city or DEFAULT_LOCATION
        url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={self.weather_key}&units=metric"
        
        try:
            response = requests.get(url, timeout=5)
            data = response.json()
            
            if response.status_code == 200:
                weather_info = {
                    'error': False,
                    'city': data['name'],
                    'country': data['sys']['country'],
                    'temperature': round(data['main']['temp'], 1),
                    'feels_like': round(data['main']['feels_like'], 1),
                    'description': data['weather'][0]['description'].capitalize(),
                    'humidity': data['main']['humidity'],
                    'wind_speed': data['wind']['speed'],
                    'icon': data['weather'][0]['icon']
                }
                return weather_info
            else:
                return {
                    'error': True,
                    'message': f"City '{city}' not found. Please check the spelling."
                }
        except Exception as e:
            return {
                'error': True,
                'message': f"Weather service unavailable: {str(e)}"
            }
    
    def format_weather_response(self, weather_data):
        """Format weather data into readable response"""
        if weather_data.get('error'):
            return weather_data['message']
        
        response = f"🌤️ Weather in {weather_data['city']}, {weather_data['country']}:\n"
        response += f"Temperature: {weather_data['temperature']}°C (Feels like {weather_data['feels_like']}°C)\n"
        response += f"Conditions: {weather_data['description']}\n"
        response += f"Humidity: {weather_data['humidity']}%\n"
        response += f"Wind Speed: {weather_data['wind_speed']} m/s"
        
        return response
    
    def get_news(self, category='general', country='us', limit=5):
        """Get latest news headlines"""
        if not self.news_key or self.news_key == 'YOUR_NEWSAPI_KEY':
            return {
                'error': True,
                'message': 'News API key not configured. Please add your NewsAPI key in config.py'
            }
        
        url = f"https://newsapi.org/v2/top-headlines?country={country}&category={category}&apiKey={self.news_key}&pageSize={limit}"
        
        try:
            response = requests.get(url, timeout=5)
            data = response.json()
            
            if response.status_code == 200 and data['status'] == 'ok':
                articles = []
                for article in data['articles']:
                    articles.append({
                        'title': article['title'],
                        'description': article.get('description', 'No description'),
                        'source': article['source']['name'],
                        'url': article['url'],
                        'published': article['publishedAt']
                    })
                
                return {
                    'error': False,
                    'articles': articles,
                    'total': data['totalResults']
                }
            else:
                return {
                    'error': True,
                    'message': 'Unable to fetch news at the moment.'
                }
        except Exception as e:
            return {
                'error': True,
                'message': f"News service unavailable: {str(e)}"
            }
    
    def format_news_response(self, news_data, limit=5):
        """Format news data into readable response"""
        if news_data.get('error'):
            return news_data['message']
        
        articles = news_data['articles'][:limit]
        response = f"📰 Latest News Headlines:\n\n"
        
        for i, article in enumerate(articles, 1):
            response += f"{i}. {article['title']}\n"
            response += f"   Source: {article['source']}\n"
            response += f"   {article['url']}\n\n"
        
        return response
    
    def search_news(self, query):
        """Search for specific news"""
        if not self.news_key or self.news_key == 'YOUR_NEWSAPI_KEY':
            return {
                'error': True,
                'message': 'News API key not configured.'
            }
        
        url = f"https://newsapi.org/v2/everything?q={query}&apiKey={self.news_key}&pageSize=5&sortBy=publishedAt"
        
        try:
            response = requests.get(url, timeout=5)
            data = response.json()
            
            if response.status_code == 200:
                return self.get_news.__wrapped__(self, data=data)
            else:
                return {'error': True, 'message': 'Search failed.'}
        except Exception as e:
            return {'error': True, 'message': str(e)}