import re
import requests
from bs4 import BeautifulSoup
import sympy as sp
import random
from datetime import datetime
from nlp_processor import NLPProcessor
from sentiment_analyzer import SentimentAnalyzer
from external_apis import ExternalAPIs
from web_search_engine import WebSearchEngine
from text_summarizer import TextSummarizer

class ChatbotAgent:
    def __init__(self):
        self.name = "ELF"
        self.full_name = "Enhanced Learning Friend"
        self.nlp = NLPProcessor()
        self.sentiment = SentimentAnalyzer()
        self.apis = ExternalAPIs()
        self.search_engine = WebSearchEngine()
        self.summarizer = TextSummarizer()
        
        # Conversation context
        self.conversation_history = []
        self.user_preferences = {}
        self.last_topic = None
        self.last_mode = 'NORMAL'
        self.conversation_depth = 0
        self.last_analysis = {}
        
        print("✅ ELF (Enhanced Learning Friend) initialized!")
        print("💬 Ready for human-like conversation!")
        
    def process_message(self, message):
        """Process message with intelligent mode detection and AI search"""
        # Store in conversation history
        self.conversation_history.append({
            'message': message,
            'timestamp': datetime.now(),
            'type': 'user'
        })
        
        # Keep only last 10 messages for context
        if len(self.conversation_history) > 10:
            self.conversation_history = self.conversation_history[-10:]
        
        # NLP Analysis
        entities = self.nlp.extract_entities(message)
        intents = self.nlp.detect_intent(message)
        sentiment_data = self.sentiment.get_detailed_sentiment(message)
        keywords = self.nlp.extract_keywords(message)
        
        # Detect mode
        mode = self.nlp.detect_mode(message)
        self.last_mode = mode
        
        # Store analysis results
        self.last_analysis = {
            'entities': entities,
            'intents': intents,
            'sentiment': sentiment_data,
            'keywords': keywords,
            'mode': mode
        }
        
        # Detect follow-up
        is_followup = self._is_followup_question(message)
        
        # Route based on mode + intent
        response = self._route_message(message, mode, intents, sentiment_data, is_followup, entities)
        
        # Add response to history
        self.conversation_history.append({
            'message': response,
            'timestamp': datetime.now(),
            'type': 'bot'
        })
        
        self.conversation_depth += 1
        return response
    
    def _is_followup_question(self, message):
        """Detect if message is a follow-up question"""
        followup_indicators = [
            'what about', 'how about', 'also', 'tell me more',
            'explain', 'elaborate', 'another', 'more', 'else',
            'can you', 'and what', 'but what'
        ]
        message_lower = message.lower()
        return any(indicator in message_lower for indicator in followup_indicators)
    
    def _route_message(self, message, mode, intents, sentiment_data, is_followup, entities):
        """Route message based on mode and intent"""
        
        # Check explicit intents first (weather, news, math, etc.)
        if 'weather' in intents:
            self.last_topic = 'weather'
            return self.handle_weather(message, entities)
        
        if 'news' in intents and mode != 'WEB_SEARCH':
            self.last_topic = 'news'
            return self.handle_news(message)
        
        if 'math' in intents:
            self.last_topic = 'math'
            return self.solve_math(message)
        
        if 'greeting' in intents and mode == 'NORMAL':
            self.last_topic = 'greeting'
            return self.greet_with_sentiment(sentiment_data)
        
        if 'farewell' in intents:
            self.last_topic = 'farewell'
            return self.farewell()
        
        if 'help' in intents:
            self.last_topic = 'help'
            return self.show_capabilities()
        
        if 'time' in intents and mode == 'NORMAL':
            self.last_topic = 'time'
            return self.get_current_time()
        
        if 'sentiment_check' in intents:
            self.last_topic = 'sentiment'
            return self.analyze_user_sentiment(sentiment_data)
        
        # Mode-based routing
        if mode == 'SUMMARIZATION':
            self.last_topic = 'summary'
            return self.handle_summarization(message)
        
        if mode == 'WEB_SEARCH' or 'web_search' in intents or 'search' in intents:
            self.last_topic = 'search'
            return self.handle_ai_search(message)
        
        # Default: conversational response
        return self.conversational_response(message, sentiment_data, is_followup)
    
    def handle_ai_search(self, message):
        """AI Search — like Google AI, search + synthesize + structured answer"""
        # Extract optimized search keywords
        query = self.nlp.extract_search_keywords(message)
        
        if not query or len(query) < 2:
            return "🤔 What would you like me to search for? Be as specific as you'd like!\n\nExample: 'What is machine learning?' or 'best Python frameworks 2024'"
        
        # Perform AI search
        search_results = self.search_engine.search_web(query, num_results=5)
        
        if search_results['success']:
            ai_answer = search_results.get('ai_answer', {})
            
            # Build structured response
            response = ""
            
            if ai_answer and ai_answer.get('answer'):
                response += f"🔎 **AI Answer:**\n{ai_answer['answer']}\n\n"
                
                if ai_answer.get('key_points'):
                    response += "📌 **Key Points:**\n"
                    for point in ai_answer['key_points']:
                        response += f"• {point}\n"
                    response += "\n"
                
                if ai_answer.get('sources'):
                    response += "🌐 **Sources:**\n"
                    for i, src in enumerate(ai_answer['sources'], 1):
                        response += f"{i}. {src['title']} — {src.get('domain', '')}\n   {src['url']}\n"
                    response += "\n"
                
                if ai_answer.get('insight'):
                    response += f"🧠 **Insight:**\n{ai_answer['insight']}"
            else:
                response = self.search_engine.format_search_results(search_results)
            
            return response
        else:
            return f"😕 I had trouble searching for '{query}'. Could you try:\n• Rephrasing your query\n• Checking your internet connection\n• Being more specific\n\nOr ask me something else!"
    
    def handle_summarization(self, message):
        """Handle text summarization with enhanced output"""
        url_pattern = r'https?://[^\s]+'
        urls = re.findall(url_pattern, message)
        
        if urls:
            url = urls[0]
            return f"📝 Fetching and summarizing content from {url}...\n\n" + self._summarize_url(url)
        else:
            text = re.sub(r'(summarize|summary|tldr|brief|sum up|key points of)', '', message, flags=re.IGNORECASE).strip()
            
            if len(text) < 50:
                return "📝 I can summarize content for you! Just:\n\n1. Paste a URL: 'summarize https://example.com'\n2. Or paste text: 'summarize: [your long text]'\n\nWhat would you like me to summarize?"
            
            # Use multi-document summary for rich output
            multi_summary = self.summarizer.multi_document_summary([text], query="")
            if multi_summary['success']:
                return self.summarizer.format_summary(multi_summary)
            
            # Fallback
            summary = self.summarizer.summarize(text, num_sentences=3)
            return self.summarizer.format_summary(summary)
    
    def _summarize_url(self, url):
        """Summarize URL content"""
        url_content = self.search_engine.fetch_page_content(url)
        if url_content['success']:
            summary = self.summarizer.summarize_url(url_content, num_sentences=3)
            return self.summarizer.format_summary(summary)
        else:
            return f"😕 I couldn't access that webpage. Make sure:\n• The URL is correct\n• The site doesn't require login\n• It's not behind a paywall\n\nWant to try another URL?"
    
    def handle_weather(self, message, entities):
        """Handle weather with conversational tone"""
        city = None
        for entity in entities:
            if entity['label'] in ['GPE', 'LOC', 'ENTITY']:
                city = entity['text']
                break
        
        # Fallback if no capitalized entity was found (e.g., lowercase input)
        if not city:
            message_lower = message.lower()
            for kw in ['weather in ', 'weather ', 'temperature in ', 'temperature ']:
                if kw in message_lower:
                    potential_city = message_lower.split(kw, 1)[1].strip().strip('?!.,')
                    if potential_city.endswith(' city'):
                        potential_city = potential_city[:-5]
                    if potential_city:
                        city = potential_city
                        break
        
        if not city:
            return "🌤️ Which city's weather would you like to know? Just tell me the city name!"
        
        weather_data = self.apis.get_weather(city)
        response = self.apis.format_weather_response(weather_data)
        
        if not weather_data.get('error'):
            temp = weather_data['temperature']
            if temp > 30:
                response += "\n\n☀️ Quite hot! Stay hydrated and avoid direct sun!"
            elif temp > 25:
                response += "\n\n🌤️ Nice and warm! Great weather for outdoor activities!"
            elif temp < 10:
                response += "\n\n🧥 Chilly! Don't forget your jacket!"
        
        return response
    
    def handle_news(self, message):
        """Handle news requests"""
        message_lower = message.lower()
        categories = ['business', 'entertainment', 'health', 'science', 'sports', 'technology']
        category = 'general'
        
        for cat in categories:
            if cat in message_lower:
                category = cat
                break
        
        news_data = self.apis.get_news(category=category)
        return self.apis.format_news_response(news_data)
    
    def analyze_user_sentiment(self, sentiment_data):
        """Provide empathetic sentiment analysis"""
        sentiment = sentiment_data['vader']['sentiment']
        compound = sentiment_data['vader']['compound']
        emoji = sentiment_data['vader']['emoji']
        
        response = f"💭 **Your Emotional State:**\n\n"
        response += f"I sense you're feeling **{sentiment}** {emoji}\n"
        response += f"Confidence Level: {abs(compound):.0%}\n\n"
        
        response += f"**Emotional Breakdown:**\n"
        response += f"• Positivity: {sentiment_data['vader']['positive']:.0%}\n"
        response += f"• Neutrality: {sentiment_data['vader']['neutral']:.0%}\n"
        response += f"• Negativity: {sentiment_data['vader']['negative']:.0%}\n\n"
        
        if sentiment == 'positive':
            response += "😊 That's wonderful! Your positive energy is contagious! Keep spreading those good vibes!"
        elif sentiment == 'negative':
            response += "💙 I understand things might be tough right now. Remember, it's okay to feel this way. I'm here if you want to talk about it."
        else:
            response += "😌 You seem calm and balanced. That's a good place to be!"
        
        return response
    
    def greet_with_sentiment(self, sentiment_data):
        """Warm, personalized greetings"""
        sentiment = sentiment_data['vader']['sentiment']
        hour = datetime.now().hour
        
        if hour < 12:
            time_greeting = "Good morning"
        elif hour < 17:
            time_greeting = "Good afternoon"
        else:
            time_greeting = "Good evening"
        
        greetings = {
            'positive': [
                f"{time_greeting}! 😊 You seem cheerful! I'm ELF, and I'm excited to help you today! What's on your mind?",
                f"Hey there! {time_greeting}! 🌟 Love your positive energy! I'm ELF — your AI search assistant. Ask me anything!",
            ],
            'negative': [
                f"{time_greeting}. I'm ELF, and I'm here for you. 💙 Whatever you need, I'll do my best to help. What can I do?",
                f"Hello. {time_greeting}. I'm ELF, your AI friend. If something's troubling you, feel free to share. I'm listening.",
            ],
            'neutral': [
                f"{time_greeting}! I'm ELF (Enhanced Learning Friend) 🤖 I can search the web like Google AI, summarize articles, check weather, get news, and more! What would you like to know?",
                f"Hi! {time_greeting}! I'm ELF, your AI search assistant! Ask me any question and I'll search, analyze, and give you a structured answer! What's on your mind? 🚀",
            ]
        }
        
        return random.choice(greetings.get(sentiment, greetings['neutral']))
    
    def farewell(self):
        """Warm goodbye messages"""
        farewells = [
            "Goodbye, friend! 👋 It's been wonderful chatting with you! Come back anytime!",
            "See you later! 🌟 Feel free to return whenever you need me. Take care!",
            "Farewell! ✨ Thanks for the great conversation! ELF is always here when you need answers!",
            "Bye for now! 💙 I hope I was helpful! Don't hesitate to come back. Stay awesome!",
        ]
        return random.choice(farewells)
    
    def solve_math(self, expression):
        """Solve math with friendly responses"""
        try:
            expression = re.sub(r'(calculate|solve|what is|compute|math)', '', expression, flags=re.IGNORECASE)
            expression = expression.replace('x', '*').replace('×', '*').replace('÷', '/')
            expression = expression.strip('? ')
            
            result = sp.sympify(expression)
            evaluated = result.evalf()
            
            return f"🔢 **Math Solution:**\n\n{expression} = **{evaluated}**\n\n✅ There's your answer! Need me to solve anything else?"
        except Exception as e:
            return f"🤔 Hmm, I had trouble solving that. Could you rephrase it? Try something like:\n• calculate 15 * 23\n• solve 2^10\n• what is 100 / 8"
    
    def get_current_time(self):
        """Get current time with personality"""
        now = datetime.now()
        date_str = now.strftime('%A, %B %d, %Y')
        time_str = now.strftime('%I:%M %p')
        
        return f"⏰ **Right now it's:**\n\n📅 {date_str}\n🕐 {time_str}\n\n💭 Time flies when you're having fun, right?"
    
    def show_capabilities(self):
        """Show capabilities with friendly tone"""
        return """👋 **Hi! I'm ELF (Enhanced Learning Friend)**

I'm your intelligent AI search assistant! Here's what I can do:

**🔎 AI Search (like Google AI)**
- Ask any question and I'll search, analyze, and synthesize answers
- Get structured responses with key points and sources
- Try: "What is quantum computing?" or "best Python frameworks"

**📝 Smart Summarization**
- Summarize articles, websites, or long text
- Get TL;DR, key points, and important keywords
- Try: "summarize https://example.com" or paste long text

**🌤️ Weather Updates**
- Real-time weather for any city worldwide
- Try: "weather in Paris"

**📰 Latest News**
- Breaking headlines by category
- Try: "technology news" or "sports news"

**🔢 Math Solver**
- Complex calculations and equations
- Try: "calculate 25 * 17 + 89"

**😊 Emotional Intelligence**
- Sentiment analysis with empathetic responses
- Try: "I'm feeling great today!"

**💬 Natural Conversation**
- Context-aware, human-like chat
- Just talk naturally!

**🎤 Voice Input & 🔊 Output**
- Speak your questions and listen to answers

I'm always here to help! What would you like to explore? 🌟"""
    
    def conversational_response(self, message, sentiment_data, is_followup):
        """Enhanced conversational responses with context"""
        sentiment = sentiment_data['vader']['sentiment']
        emoji = sentiment_data['vader']['emoji']
        message_lower = message.lower()
        
        # Empathetic acknowledgment
        sentiment_responses = {
            'positive': ["That's great!", "Wonderful!", "Awesome!", "I love that!"],
            'negative': ["I understand.", "I hear you.", "That's tough.", "I'm sorry to hear that."],
            'neutral': ["I see.", "Okay.", "Got it.", "Alright."]
        }
        
        acknowledgment = random.choice(sentiment_responses[sentiment])
        
        # Specific responses
        responses = {
            "how are you": f"I'm doing fantastic, thanks for asking! {emoji} I'm always excited to help! How are YOU doing?",
            "thank": f"{acknowledgment} You're very welcome! It's my pleasure to help! Need anything else? 😊",
            "joke": "Haha! Want to hear one? Why did the AI cross the road? To optimize the other side! 😄 Got any more requests?",
            "love": f"Aww, that's so sweet! {emoji} I'm glad I could help! What else can I do for you?",
            "awesome": f"Right?! {emoji} I'm excited too! What's next on your mind?",
            "smart": "Thank you! I try my best! 😊 But I'm only as good as my ability to help YOU. What do you need?",
            "who are you": "I'm ELF — Enhanced Learning Friend! 🧝 I'm your AI search assistant. I can search the web, summarize content, check weather, solve math, and more! What would you like to know?",
            "your name": "I'm ELF — Enhanced Learning Friend! 🧝 Think of me as your personal AI research assistant. Ask me anything!",
        }
        
        for key, response in responses.items():
            if key in message_lower:
                return f"{acknowledgment} {emoji} {response}"
        
        # Context-aware responses
        if is_followup and self.last_topic:
            if self.last_topic == 'search':
                return f"{acknowledgment} Want me to search for something else? Or summarize any of those results? Just let me know!"
            elif self.last_topic == 'weather':
                return f"{acknowledgment} Need weather for another location? Or something completely different? I'm here!"
            elif self.last_topic == 'news':
                return f"{acknowledgment} Want news from a different category? Or shall we explore something else?"
        
        # Extract keywords for intelligent response
        keywords = self.nlp.extract_keywords(message)
        
        if keywords:
            key_topics = ', '.join(keywords[:2])
            return f"{acknowledgment} {emoji} I see you're interested in: **{key_topics}**. I can help you:\n\n🔎 Search for information about this\n📝 Summarize articles\n💬 Discuss it further\n🌐 Find related resources\n\nWhat would you like to do?"
        
        # Friendly default response
        friendly_defaults = [
            f"{acknowledgment} {emoji} I'm here to help! Ask me any question and I'll search the web for an AI-powered answer, or I can summarize content, check weather, get news, and more!",
            f"{acknowledgment} {emoji} Tell me more! Try asking a question like 'What is blockchain?' and I'll give you a structured AI answer with sources!",
            f"{acknowledgment} {emoji} I'm your AI search assistant! Ask me anything — from factual questions to how-to guides — and I'll find the answer! 🔎",
        ]
        
        return random.choice(friendly_defaults)
    
    def get_last_analysis(self):
        """Return the last NLP analysis"""
        return self.last_analysis
    
    def get_conversation_context(self):
        """Get conversation context"""
        return {
            'history': self.conversation_history[-5:],
            'last_topic': self.last_topic,
            'depth': self.conversation_depth,
            'last_mode': self.last_mode
        }