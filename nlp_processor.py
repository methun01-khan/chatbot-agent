import nltk
from nltk.tokenize import word_tokenize
from collections import Counter
import re

# Download required NLTK data
try:
    nltk.download('punkt', quiet=True)
    nltk.download('punkt_tab', quiet=True)
    nltk.download('stopwords', quiet=True)
    nltk.download('averaged_perceptron_tagger', quiet=True)
except:
    pass

class NLPProcessor:
    def __init__(self):
        try:
            from nltk.corpus import stopwords
            self.stop_words = set(stopwords.words('english'))
        except:
            self.stop_words = set(['the', 'is', 'at', 'which', 'on', 'a', 'an', 'and', 'or', 'but'])
        
        # Search trigger words
        self.search_triggers = [
            'what is', 'what are', 'who is', 'who are', 'where is', 'when did',
            'how does', 'how do', 'how to', 'why does', 'why do', 'why is',
            'explain', 'define', 'tell me about', 'information about',
            'latest', 'current', 'recent', 'today', 'news about',
            'best', 'top', 'recommend', 'compare', 'difference between',
            'pros and cons', 'advantages', 'disadvantages',
            'price of', 'cost of', 'how much', 'when was',
            'capital of', 'population of', 'meaning of',
            'search for', 'find', 'look up', 'google', 'search', 'look for', 'find me'
        ]
        
        print("✅ NLP Processor initialized (with Search & Summary support)!")
    
    def detect_mode(self, text):
        """Detect whether input should use SUMMARIZATION, WEB_SEARCH, or NORMAL mode"""
        text_lower = text.lower().strip()
        word_count = len(text.split())
        
        # MODE 1: SUMMARIZATION — long text pasted
        if word_count > 80:
            return 'SUMMARIZATION'
        
        # Check for explicit summarize commands
        summarize_keywords = ['summarize', 'summary', 'tldr', 'tl;dr', 'sum up', 'key points of', 'brief of']
        if any(kw in text_lower for kw in summarize_keywords):
            return 'SUMMARIZATION'
        
        # Check for URL — likely wants summarization
        if re.search(r'https?://[^\s]+', text):
            return 'SUMMARIZATION'
        
        # MODE 2: WEB_SEARCH — questions needing factual/latest info
        # Explicit search commands
        search_commands = ['search for', 'search about', 'find me', 'look up', 'google']
        if any(text_lower.startswith(cmd) or cmd in text_lower for cmd in search_commands):
            return 'WEB_SEARCH'
        
        # Question patterns that need real-world knowledge
        question_patterns = [
            r'^(what|who|where|when|which|how|why)\s',
            r'\?$',
            r'(tell me about|explain|define|describe)\s',
            r'(latest|current|recent|today|new)\s.*(news|update|development|trend)',
            r'(best|top|recommend|popular)\s',
            r'(price|cost|worth|salary|population|capital)\s(of|in|for)',
            r'(difference|compare|vs|versus)\s',
            r'(how to|how do|how does|how can)\s',
            r'(what is|what are|what was|what were)\s',
            r'(who is|who are|who was|who were)\s',
        ]
        for pattern in question_patterns:
            if re.search(pattern, text_lower):
                # But skip simple chatbot questions
                simple_chat = ['how are you', 'what is your name', 'who are you', 
                             'what can you do', 'how do you work', 'what time']
                if not any(sc in text_lower for sc in simple_chat):
                    return 'WEB_SEARCH'
        
        # MODE 3: NORMAL — greetings, chat, simple commands
        return 'NORMAL'
    
    def extract_search_keywords(self, text):
        """Extract optimized search keywords from natural language query"""
        text_lower = text.lower().strip()
        
        # Remove common filler phrases
        filler_phrases = [
            'search for', 'search about', 'find me', 'look up', 'google',
            'can you tell me', 'tell me about', 'i want to know',
            'please', 'could you', 'would you', 'can you',
            'i need information about', 'information about',
            'what do you know about', 'explain to me',
            'help me understand', 'help me find',
        ]
        cleaned = text_lower
        for phrase in filler_phrases:
            cleaned = cleaned.replace(phrase, '')
        cleaned = cleaned.strip(' ?!.,')
        
        # If cleaned is too short, use original minus basic fillers
        if len(cleaned) < 3:
            cleaned = re.sub(r'^(search|find|google|look up)\s+', '', text_lower).strip(' ?!.,')
        
        return cleaned if cleaned else text_lower
    
    def extract_entities(self, text):
        """Extract basic entities from text"""
        entities = []
        
        # Extract capitalized words (likely names/places)
        words = text.split()
        for i, word in enumerate(words):
            if word and word[0].isupper() and i > 0:
                entities.append({
                    'text': word,
                    'label': 'ENTITY',
                    'description': 'Capitalized word (possible name/place)'
                })
        
        # Extract dates
        date_pattern = r'\b\d{1,2}[-/]\d{1,2}[-/]\d{2,4}\b|\b(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]* \d{1,2},? \d{4}\b'
        dates = re.findall(date_pattern, text, re.IGNORECASE)
        for date in dates:
            entities.append({
                'text': date,
                'label': 'DATE',
                'description': 'Date reference'
            })
        
        # Extract URLs
        url_pattern = r'https?://[^\s]+'
        urls = re.findall(url_pattern, text)
        for url in urls:
            entities.append({
                'text': url,
                'label': 'URL',
                'description': 'Web URL'
            })
        
        return entities
    
    def extract_keywords(self, text, top_n=5):
        """Extract keywords from text"""
        try:
            words = word_tokenize(text.lower())
        except:
            words = text.lower().split()
        
        words = [word for word in words if word.isalnum() and word not in self.stop_words and len(word) > 2]
        
        word_freq = Counter(words)
        keywords = [word for word, freq in word_freq.most_common(top_n)]
        
        return keywords
    
    def get_pos_tags(self, text):
        """Get part-of-speech tags (simplified)"""
        try:
            words = word_tokenize(text)
            pos_tags = nltk.pos_tag(words)
            
            return [{'word': word, 'pos': pos, 'tag': pos} for word, pos in pos_tags]
        except:
            return []
    
    def detect_intent(self, text):
        """Detect user intent from text"""
        text_lower = text.lower()
        
        intents = {
            'web_search': ['search for', 'find', 'look up', 'google', 'search', 'look for', 'find me'],
            'summarize': ['summarize', 'summary', 'tldr', 'brief', 'sum up', 'give me a summary', 'key points'],
            'weather': ['weather', 'temperature', 'forecast', 'rain', 'sunny', 'cloudy', 'hot', 'cold', 'climate'],
            'news': ['news', 'headlines', 'happening', 'current events'],
            'greeting': ['hello', 'hi', 'hey', 'greetings', 'good morning', 'good evening', 'good afternoon'],
            'farewell': ['bye', 'goodbye', 'see you', 'farewell', 'exit', 'quit', 'leave'],
            'math': ['calculate', 'solve', 'compute', 'math', 'equation'],
            'help': ['help', 'what can you do', 'capabilities', 'features', 'commands'],
            'time': ['what time', 'current time', 'what date', 'today date'],
            'sentiment_check': ['how do i feel', 'my mood', 'analyze my message', 'sentiment', 'analyze my mood']
        }
        
        detected_intents = []
        for intent, keywords in intents.items():
            if any(keyword in text_lower for keyword in keywords):
                detected_intents.append(intent)
        
        return detected_intents if detected_intents else ['general']
    
    def analyze_sentence_structure(self, text):
        """Analyze sentence structure (simplified)"""
        sentences = text.split('.')
        words = text.split()
        
        return {
            'num_sentences': len([s for s in sentences if s.strip()]),
            'num_words': len(words),
            'avg_word_length': sum(len(w) for w in words) / len(words) if words else 0
        }