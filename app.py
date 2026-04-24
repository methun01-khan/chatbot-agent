from flask import Flask, render_template, request, jsonify, send_file
from flask_cors import CORS
import speech_recognition as sr
from gtts import gTTS
import os
import tempfile
from database import Database
from chatbot_agent import ChatbotAgent
from config import FLASK_CONFIG

app = Flask(__name__)
CORS(app)

# Initialize components
db = Database()
chatbot = ChatbotAgent()
recognizer = sr.Recognizer()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/chat', methods=['POST'])
def chat():
    try:
        data = request.json
        user_message = data.get('message', '')
        
        if not user_message:
            return jsonify({'error': 'No message provided'}), 400
        
        # Process message through chatbot agent
        bot_response = chatbot.process_message(user_message)
        
        # Get NLP analysis
        analysis = chatbot.get_last_analysis()
        
        # Save to database with sentiment
        sentiment_data = analysis.get('sentiment', {}).get('vader', {})
        db.save_conversation(
            user_message, 
            bot_response,
            sentiment_data.get('sentiment'),
            sentiment_data.get('compound'),
            analysis.get('entities')
        )
        
        # Save sentiment analytics
        if sentiment_data:
            db.save_sentiment_analytics(user_message, sentiment_data)
        
        return jsonify({
            'response': bot_response,
            'analysis': {
                'sentiment': sentiment_data.get('sentiment'),
                'entities': analysis.get('entities', []),
                'intents': analysis.get('intents', []),
                'keywords': analysis.get('keywords', []),
                'mode': analysis.get('mode', 'NORMAL')
            }
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/ai-search', methods=['POST'])
def ai_search():
    """Dedicated AI search endpoint returning structured JSON"""
    try:
        data = request.json
        query = data.get('query', '')
        num_results = data.get('num_results', 5)
        
        if not query:
            return jsonify({'error': 'No query provided'}), 400
        
        # Extract search keywords
        search_query = chatbot.nlp.extract_search_keywords(query)
        
        # Perform search
        search_results = chatbot.search_engine.search_web(search_query, num_results=num_results)
        
        if search_results['success']:
            ai_answer = search_results.get('ai_answer', {})
            return jsonify({
                'success': True,
                'query': search_query,
                'answer': ai_answer.get('answer', ''),
                'key_points': ai_answer.get('key_points', []),
                'sources': ai_answer.get('sources', []),
                'insight': ai_answer.get('insight', ''),
                'results': search_results.get('results', []),
                'count': search_results.get('count', 0)
            })
        else:
            return jsonify({
                'success': False,
                'error': search_results.get('error', 'Search failed'),
                'query': search_query
            })
    
    except Exception as e:
        return jsonify({'error': str(e), 'success': False}), 500

@app.route('/web-search', methods=['POST'])
def web_search():
    """Web search endpoint"""
    try:
        data = request.json
        query = data.get('query', '')
        num_results = data.get('num_results', 5)
        
        if not query:
            return jsonify({'error': 'No query provided', 'success': False}), 400
        
        search_results = chatbot.search_engine.search_web(query, num_results=num_results)
        
        return jsonify({
            'success': search_results.get('success', False),
            'query': query,
            'results': search_results.get('results', []),
            'count': search_results.get('count', 0),
            'ai_answer': search_results.get('ai_answer', {}),
            'timestamp': search_results.get('timestamp', '')
        })
    
    except Exception as e:
        return jsonify({'error': str(e), 'success': False}), 500

@app.route('/summarize', methods=['POST'])
def summarize():
    """Text/URL summarization endpoint"""
    try:
        data = request.json
        url = data.get('url', '')
        text = data.get('text', '')
        num_sentences = data.get('num_sentences', 3)
        method = data.get('method', 'extractive')
        
        if url:
            # Summarize URL
            url_content = chatbot.search_engine.fetch_page_content(url)
            if url_content['success']:
                summary = chatbot.summarizer.summarize_url(url_content, num_sentences=num_sentences)
                return jsonify(summary)
            else:
                return jsonify({'success': False, 'error': 'Could not fetch URL content'})
        elif text:
            # Summarize text
            summary = chatbot.summarizer.summarize(text, num_sentences=num_sentences, method=method)
            return jsonify(summary)
        else:
            return jsonify({'success': False, 'error': 'No text or URL provided'}), 400
    
    except Exception as e:
        return jsonify({'error': str(e), 'success': False}), 500

@app.route('/text-to-speech', methods=['POST'])
def text_to_speech():
    try:
        data = request.json
        text = data.get('text', '')
        
        if not text:
            return jsonify({'error': 'No text provided'}), 400
        
        # Generate speech
        tts = gTTS(text=text, lang='en', slow=False)
        
        # Save to temporary file
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.mp3')
        tts.save(temp_file.name)
        
        return send_file(temp_file.name, mimetype='audio/mpeg')
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/analyze-sentiment', methods=['POST'])
def analyze_sentiment():
    try:
        data = request.json
        text = data.get('text', '')
        
        if not text:
            return jsonify({'error': 'No text provided'}), 400
        
        sentiment_data = chatbot.sentiment.get_detailed_sentiment(text)
        
        return jsonify(sentiment_data)
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/history', methods=['GET'])
def get_history():
    try:
        limit = request.args.get('limit', 10, type=int)
        history = db.get_conversation_history(limit)
        return jsonify({'history': history})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/sentiment-stats', methods=['GET'])
def sentiment_stats():
    try:
        stats = db.get_sentiment_stats()
        return jsonify({'stats': stats})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/search-history', methods=['GET'])
def search_history():
    try:
        limit = request.args.get('limit', 10, type=int)
        searches = db.get_recent_searches(limit)
        return jsonify({'searches': searches})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/summary-history', methods=['GET'])
def summary_history():
    try:
        limit = request.args.get('limit', 10, type=int)
        summaries = db.get_recent_summaries(limit)
        return jsonify({'summaries': summaries})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/weather/<city>', methods=['GET'])
def get_weather(city):
    try:
        weather_data = chatbot.apis.get_weather(city)
        return jsonify(weather_data)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/news', methods=['GET'])
def get_news():
    try:
        category = request.args.get('category', 'general')
        news_data = chatbot.apis.get_news(category=category)
        return jsonify(news_data)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    print("🚀 Starting Advanced AI Chatbot Agent...")
    print("📍 Visit: http://localhost:5000")
    print("✨ Features: AI Search, NLP, Summarization, Sentiment, Weather, News, TTS")
    app.run(**FLASK_CONFIG)