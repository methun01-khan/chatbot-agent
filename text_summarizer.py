from collections import Counter
import re
import nltk
from textblob import TextBlob

try:
    nltk.download('punkt', quiet=True)
    nltk.download('punkt_tab', quiet=True)
    nltk.download('stopwords', quiet=True)
except:
    pass

class TextSummarizer:
    def __init__(self):
        try:
            from nltk.corpus import stopwords
            self.stop_words = set(stopwords.words('english'))
        except:
            self.stop_words = set(['the', 'is', 'at', 'which', 'on', 'a', 'an'])
        
        print("✅ Text Summarizer initialized!")
    
    def summarize(self, text, num_sentences=3, method='extractive'):
        """Summarize text using specified method"""
        if method == 'extractive':
            return self.extractive_summary(text, num_sentences)
        elif method == 'abstractive':
            return self.abstractive_summary(text, num_sentences)
        else:
            return self.extractive_summary(text, num_sentences)
    
    def extractive_summary(self, text, num_sentences=3):
        """Extract most important sentences from text"""
        try:
            sentences = self._split_sentences(text)
            
            if len(sentences) <= num_sentences:
                return {
                    'success': True,
                    'summary': text,
                    'original_length': len(text),
                    'summary_length': len(text),
                    'compression_ratio': 1.0,
                    'method': 'extractive',
                    'note': 'Text is already short'
                }
            
            sentence_scores = self._score_sentences(sentences)
            
            top_sentences = sorted(sentence_scores.items(), 
                                  key=lambda x: x[1], 
                                  reverse=True)[:num_sentences]
            
            # Sort by original order
            top_sentences = sorted(top_sentences, 
                                  key=lambda x: sentences.index(x[0]))
            
            summary = ' '.join([sent for sent, score in top_sentences])
            
            return {
                'success': True,
                'summary': summary,
                'original_length': len(text),
                'summary_length': len(summary),
                'compression_ratio': round(len(summary) / len(text), 2),
                'method': 'extractive',
                'num_sentences': len(top_sentences)
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'summary': text[:500]
            }
    
    def abstractive_summary(self, text, max_length=150):
        """Generate abstractive summary (simplified version)"""
        try:
            blob = TextBlob(text)
            noun_phrases = list(blob.noun_phrases)[:5]
            
            sentences = self._split_sentences(text)
            sentence_scores = self._score_sentences(sentences)
            
            top_sentence = max(sentence_scores.items(), key=lambda x: x[1])[0]
            
            if noun_phrases:
                summary = f"Key topics: {', '.join(noun_phrases[:3])}. {top_sentence}"
            else:
                summary = top_sentence
            
            if len(summary) > max_length:
                summary = summary[:max_length] + '...'
            
            return {
                'success': True,
                'summary': summary,
                'original_length': len(text),
                'summary_length': len(summary),
                'compression_ratio': round(len(summary) / len(text), 2),
                'method': 'abstractive',
                'key_phrases': noun_phrases[:5]
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'summary': text[:max_length]
            }
    
    def multi_document_summary(self, texts, query="", num_points=5):
        """Summarize content from multiple sources (for AI search)"""
        try:
            # Combine all texts
            combined = ' '.join(texts)
            
            # Get sentences
            sentences = self._split_sentences(combined)
            
            if not sentences:
                return {
                    'success': False,
                    'error': 'No content to summarize',
                    'tldr': '',
                    'summary': '',
                    'key_points': [],
                    'keywords': []
                }
            
            # Score sentences
            sentence_scores = self._score_sentences(sentences)
            
            # Boost sentences relevant to query
            if query:
                query_words = set(query.lower().split())
                for sent in sentence_scores:
                    sent_words = set(sent.lower().split())
                    overlap = len(query_words & sent_words)
                    sentence_scores[sent] += overlap * 0.5
            
            # Sort by score
            ranked = sorted(sentence_scores.items(), key=lambda x: x[1], reverse=True)
            
            # TL;DR — single best sentence
            tldr = ranked[0][0] if ranked else ''
            
            # Detailed summary — top 3 sentences in original order
            top_3 = ranked[:3]
            top_3_ordered = sorted(top_3, key=lambda x: sentences.index(x[0]) if x[0] in sentences else 0)
            summary = ' '.join([s[0] for s in top_3_ordered])
            
            # Key points — top N unique sentences
            key_points = []
            seen = set()
            for sent, score in ranked:
                cleaned = sent.strip()
                if cleaned and len(cleaned) > 20 and cleaned not in seen:
                    key_points.append(cleaned)
                    seen.add(cleaned)
                if len(key_points) >= num_points:
                    break
            
            # Extract important keywords
            all_words = []
            for sent in sentences:
                words = re.findall(r'\w+', sent.lower())
                all_words.extend([w for w in words if w not in self.stop_words and len(w) > 3])
            
            word_freq = Counter(all_words)
            keywords = [word for word, count in word_freq.most_common(10)]
            
            return {
                'success': True,
                'tldr': tldr,
                'summary': summary,
                'key_points': key_points,
                'keywords': keywords,
                'original_length': len(combined),
                'num_sources': len(texts)
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'tldr': '',
                'summary': '',
                'key_points': [],
                'keywords': []
            }
    
    def _split_sentences(self, text):
        """Split text into sentences"""
        try:
            from nltk.tokenize import sent_tokenize
            return sent_tokenize(text)
        except:
            sentences = re.split(r'[.!?]+', text)
            return [s.strip() for s in sentences if s.strip()]
    
    def _score_sentences(self, sentences):
        """Score sentences based on word frequency"""
        all_words = []
        for sentence in sentences:
            words = re.findall(r'\w+', sentence.lower())
            all_words.extend([w for w in words if w not in self.stop_words])
        
        word_freq = Counter(all_words)
        
        sentence_scores = {}
        for sentence in sentences:
            words = re.findall(r'\w+', sentence.lower())
            words = [w for w in words if w not in self.stop_words]
            
            if words:
                score = sum(word_freq[word] for word in words) / len(words)
                sentence_scores[sentence] = score
        
        return sentence_scores
    
    def summarize_url(self, url_content, num_sentences=3):
        """Summarize content fetched from URL"""
        if not url_content.get('success'):
            return {
                'success': False,
                'error': 'Could not fetch URL content'
            }
        
        text = url_content['content']
        summary = self.extractive_summary(text, num_sentences)
        
        if summary['success']:
            summary['title'] = url_content.get('title', 'No title')
            summary['url'] = url_content.get('url', '')
        
        return summary
    
    def get_key_points(self, text, num_points=5):
        """Extract key points from text"""
        try:
            sentences = self._split_sentences(text)
            sentence_scores = self._score_sentences(sentences)
            
            top_sentences = sorted(sentence_scores.items(), 
                                  key=lambda x: x[1], 
                                  reverse=True)[:num_points]
            
            key_points = [sent for sent, score in top_sentences]
            
            return {
                'success': True,
                'key_points': key_points,
                'num_points': len(key_points)
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def format_summary(self, summary_data):
        """Format summary for display"""
        if not summary_data.get('success'):
            return f"❌ Summarization failed: {summary_data.get('error', 'Unknown error')}"
        
        output = "📝 **Text Summary**\n\n"
        
        if 'title' in summary_data:
            output += f"**Title:** {summary_data['title']}\n"
            output += f"**URL:** {summary_data['url']}\n\n"
        
        # TL;DR if available
        if summary_data.get('tldr'):
            output += f"**📋 TL;DR:**\n{summary_data['tldr']}\n\n"
        
        output += f"**Summary ({summary_data.get('method', 'extractive')} method):**\n"
        output += f"{summary_data['summary']}\n\n"
        
        # Key points if available
        if summary_data.get('key_points'):
            output += "**📌 Key Points:**\n"
            for point in summary_data['key_points']:
                output += f"• {point}\n"
            output += "\n"
        
        # Keywords if available
        if summary_data.get('keywords'):
            output += f"**🔑 Keywords:** {', '.join(summary_data['keywords'][:7])}\n\n"
        
        output += f"**Statistics:**\n"
        output += f"• Original length: {summary_data.get('original_length', 0)} characters\n"
        output += f"• Summary length: {summary_data.get('summary_length', len(summary_data.get('summary', '')))} characters\n"
        
        if summary_data.get('compression_ratio'):
            output += f"• Compression: {summary_data['compression_ratio']*100:.0f}% of original\n"
        
        if 'key_phrases' in summary_data:
            output += f"\n**Key Phrases:** {', '.join(summary_data['key_phrases'])}\n"
        
        return output