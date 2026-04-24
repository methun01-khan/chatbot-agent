import requests
from bs4 import BeautifulSoup
from urllib.parse import quote_plus, urlparse
import re
from datetime import datetime
import time

class WebSearchEngine:
    def __init__(self):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'DNT': '1',
            'Connection': 'keep-alive',
        }
        self.session = requests.Session()
        self.session.headers.update(self.headers)
        
        # Initialize DuckDuckGo search
        self.ddgs = None
        try:
            from duckduckgo_search import DDGS
            self.ddgs = DDGS()
            print("✅ Web Search Engine initialized with DuckDuckGo API!")
        except Exception as e:
            print(f"⚠️ DuckDuckGo API not available ({e}), falling back to scraping")
            print("✅ Web Search Engine initialized with Google Search!")
    
    def search_web(self, query, num_results=5):
        """Search the web and return results with deep content extraction"""
        try:
            # Step 1: Get search results
            results = []
            
            # Try DuckDuckGo API first
            if self.ddgs:
                results = self._ddgs_api_search(query, num_results)
            
            # Fallback to Google scraping
            if not results:
                results = self._google_search(query, num_results)
            
            if not results:
                return {
                    'success': False,
                    'error': 'No results found',
                    'query': query,
                    'results': [],
                    'ai_answer': None
                }
            
            # Step 2: Fetch content from top results for AI synthesis
            enriched_results = self._enrich_results_with_content(results[:3])
            
            # Step 3: Generate AI-synthesized answer
            ai_answer = self._generate_ai_answer(query, enriched_results)
            
            return {
                'success': True,
                'query': query,
                'results': results,
                'enriched_results': enriched_results,
                'count': len(results),
                'ai_answer': ai_answer,
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            print(f"Search error: {e}")
            import traceback
            traceback.print_exc()
            return {
                'success': False,
                'error': str(e),
                'query': query,
                'results': [],
                'ai_answer': None
            }
    
    def _ddgs_api_search(self, query, num_results=5):
        """Search using DuckDuckGo API (duckduckgo-search library)"""
        try:
            from duckduckgo_search import DDGS
            with DDGS() as ddgs:
                raw_results = list(ddgs.text(query, max_results=num_results))
            
            results = []
            for r in raw_results:
                url = r.get('href', r.get('url', ''))
                domain = urlparse(url).netloc if url else ''
                results.append({
                    'title': r.get('title', 'No title'),
                    'url': url,
                    'snippet': r.get('body', r.get('snippet', 'No description available')),
                    'domain': domain,
                    'source': 'DuckDuckGo'
                })
            
            return results
        except Exception as e:
            print(f"DuckDuckGo API search error: {e}")
            import traceback
            traceback.print_exc()
            return []
    
    def _google_search(self, query, num_results=5):
        """Fallback: Perform Google search via scraping"""
        try:
            search_url = f"https://www.google.com/search?q={quote_plus(query)}&num={num_results}"
            time.sleep(0.5)
            response = self.session.get(search_url, timeout=10)
            
            if response.status_code != 200:
                return []
            
            soup = BeautifulSoup(response.text, 'html.parser')
            results = []
            
            search_divs = soup.find_all('div', class_='g')
            
            for div in search_divs[:num_results]:
                try:
                    title_elem = div.find('h3')
                    if not title_elem:
                        continue
                    title = title_elem.get_text(strip=True)
                    
                    link_elem = div.find('a')
                    if not link_elem or not link_elem.get('href'):
                        continue
                    url = link_elem['href']
                    
                    if url.startswith('/url?q='):
                        url = url.split('/url?q=')[1].split('&')[0]
                    
                    snippet_elem = div.find('div', class_=['VwiC3b', 'yXK7lf', 'lVm3ye'])
                    if not snippet_elem:
                        snippet_elem = div.find('span', class_=['aCOpRe', 'st'])
                    
                    snippet = snippet_elem.get_text(strip=True) if snippet_elem else "No description available"
                    domain = urlparse(url).netloc
                    
                    results.append({
                        'title': title,
                        'url': url,
                        'snippet': snippet,
                        'domain': domain,
                        'source': 'Google'
                    })
                except:
                    continue
            
            return results
        except Exception as e:
            print(f"Google search error: {e}")
            return []
    
    def _enrich_results_with_content(self, results):
        """Fetch and extract content from top search result pages"""
        enriched = []
        for result in results[:3]:
            try:
                content_data = self.fetch_page_content(result['url'])
                if content_data['success']:
                    result['full_content'] = content_data['content'][:5000]
                    result['page_title'] = content_data.get('title', result['title'])
                else:
                    result['full_content'] = result.get('snippet', '')
                enriched.append(result)
            except:
                result['full_content'] = result.get('snippet', '')
                enriched.append(result)
        return enriched
    
    def _generate_ai_answer(self, query, enriched_results):
        """Generate a structured AI answer by synthesizing content from multiple sources"""
        if not enriched_results:
            return {
                'answer': f"I couldn't find reliable information about '{query}'. Please try rephrasing your question.",
                'key_points': [],
                'sources': [],
                'insight': 'No data available for synthesis.'
            }
        
        # Combine all content
        all_content = []
        sources = []
        all_snippets = []
        
        for r in enriched_results:
            content = r.get('full_content', r.get('snippet', ''))
            if content:
                all_content.append(content)
                all_snippets.append(r.get('snippet', ''))
            sources.append({
                'title': r['title'],
                'url': r['url'],
                'domain': r.get('domain', '')
            })
        
        combined_text = ' '.join(all_content)
        
        # Extract sentences from combined content
        sentences = self._extract_sentences(combined_text)
        
        # Score sentences by relevance to query
        query_words = set(re.findall(r'\w+', query.lower()))
        scored_sentences = []
        for sent in sentences:
            sent_clean = sent.strip()
            if len(sent_clean) < 20 or len(sent_clean) > 500:
                continue
            words = set(re.findall(r'\w+', sent_clean.lower()))
            relevance = len(query_words & words) / max(len(query_words), 1)
            # Boost sentences that look like definitions or answers
            if any(sent_clean.lower().startswith(w) for w in ['it is', 'this is', 'a ', 'an ', 'the ']):
                relevance += 0.2
            if '?' not in sent_clean:
                relevance += 0.1
            scored_sentences.append((sent_clean, relevance))
        
        scored_sentences.sort(key=lambda x: x[1], reverse=True)
        
        # Build the AI answer
        top_sentences = [s[0] for s in scored_sentences[:5]]
        
        # Create main answer from top relevant sentences
        if top_sentences:
            answer = ' '.join(top_sentences[:3])
        else:
            answer = ' '.join(all_snippets[:3])
        
        # Clean up the answer
        answer = self._clean_text(answer)
        if len(answer) > 800:
            answer = answer[:800].rsplit('.', 1)[0] + '.'
        
        # Extract key points
        key_points = []
        seen = set()
        for sent, score in scored_sentences[:8]:
            cleaned = self._clean_text(sent)
            if cleaned and len(cleaned) > 15 and cleaned not in seen:
                # Truncate long points
                if len(cleaned) > 200:
                    cleaned = cleaned[:200].rsplit(' ', 1)[0] + '...'
                key_points.append(cleaned)
                seen.add(cleaned)
            if len(key_points) >= 5:
                break
        
        # If not enough key points, use snippets
        if len(key_points) < 3:
            for snippet in all_snippets:
                cleaned = self._clean_text(snippet)
                if cleaned and cleaned not in seen:
                    if len(cleaned) > 200:
                        cleaned = cleaned[:200].rsplit(' ', 1)[0] + '...'
                    key_points.append(cleaned)
                    seen.add(cleaned)
                if len(key_points) >= 4:
                    break
        
        # Generate insight
        insight = self._generate_insight(query, top_sentences, enriched_results)
        
        return {
            'answer': answer,
            'key_points': key_points,
            'sources': sources,
            'insight': insight
        }
    
    def _extract_sentences(self, text):
        """Extract clean sentences from text"""
        text = re.sub(r'\s+', ' ', text)
        sentences = re.split(r'(?<=[.!?])\s+', text)
        clean = []
        for s in sentences:
            s = s.strip()
            if len(s) > 15 and not s.startswith('{') and not s.startswith('<'):
                clean.append(s)
        return clean
    
    def _clean_text(self, text):
        """Clean extracted text"""
        text = re.sub(r'\s+', ' ', text).strip()
        # Remove navigation/menu-like text
        if text.count('|') > 2 or text.count('►') > 1:
            return ''
        return text.strip()
    
    def _generate_insight(self, query, top_sentences, results):
        """Generate a simple insight summary"""
        num_sources = len(results)
        query_lower = query.lower()
        
        if any(w in query_lower for w in ['what is', 'define', 'meaning']):
            return f"Based on {num_sources} sources, this is a well-documented topic. The information above provides a comprehensive definition and context."
        elif any(w in query_lower for w in ['how to', 'tutorial', 'guide', 'steps']):
            return f"Compiled from {num_sources} sources. Follow the key points above for a step-by-step approach. Consider checking the source links for detailed tutorials."
        elif any(w in query_lower for w in ['best', 'top', 'recommend']):
            return f"Recommendations gathered from {num_sources} sources. Results may vary based on your specific needs and preferences."
        elif any(w in query_lower for w in ['vs', 'compare', 'difference']):
            return f"Comparison synthesized from {num_sources} sources. Each option has its strengths - review the key points to determine the best fit for your use case."
        elif any(w in query_lower for w in ['news', 'latest', 'recent', 'update']):
            return f"Latest information compiled from {num_sources} sources. For the most current updates, check the source links directly."
        else:
            return f"Information synthesized from {num_sources} reliable sources. Check the source links for deeper details."
    
    def fetch_page_content(self, url):
        """Fetch and extract text content from a webpage"""
        try:
            response = self.session.get(url, timeout=10)
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Remove unwanted elements
            for tag in soup(['script', 'style', 'nav', 'footer', 'header', 'aside', 'iframe', 'form', 'noscript']):
                tag.decompose()
            
            # Try to find main content area
            main_content = soup.find('main') or soup.find('article') or soup.find('div', class_=re.compile(r'(content|article|post|entry|main)', re.I))
            
            if main_content:
                text = main_content.get_text(separator=' ', strip=True)
            else:
                text = soup.get_text(separator=' ', strip=True)
            
            text = re.sub(r'\s+', ' ', text).strip()
            title = soup.title.string if soup.title else 'No title'
            
            return {
                'success': True,
                'url': url,
                'content': text[:10000],
                'title': title,
                'length': len(text)
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'url': url
            }
    
    def format_search_results(self, search_data):
        """Format search results with AI answer for chat display"""
        if not search_data['success']:
            return f"❌ Search failed: {search_data.get('error', 'Unknown error')}\n\nTip: Try rephrasing your query or check your internet connection."
        
        if not search_data['results']:
            return f"🔍 No results found for '{search_data['query']}'\n\nTry:\n• Using different keywords\n• Being more specific\n• Checking spelling"
        
        ai = search_data.get('ai_answer', {})
        output = ""
        
        if ai and ai.get('answer'):
            output += f"🔎 **AI Answer:**\n{ai['answer']}\n\n"
            
            if ai.get('key_points'):
                output += "📌 **Key Points:**\n"
                for point in ai['key_points']:
                    output += f"• {point}\n"
                output += "\n"
            
            if ai.get('sources'):
                output += "🌐 **Sources:**\n"
                for i, src in enumerate(ai['sources'], 1):
                    output += f"{i}. {src['title']} — {src.get('domain', '')}\n   {src['url']}\n"
                output += "\n"
            
            if ai.get('insight'):
                output += f"🧠 **Insight:**\n{ai['insight']}\n"
        else:
            output += f"🔍 Found {len(search_data['results'])} results for '{search_data['query']}':\n\n"
            for i, result in enumerate(search_data['results'], 1):
                output += f"**{i}. {result['title']}**\n"
                output += f"   🌐 {result['domain']}\n"
                output += f"   🔗 {result['url']}\n"
                if result['snippet']:
                    output += f"   📝 {result['snippet'][:200]}\n"
                output += "\n"
        
        return output