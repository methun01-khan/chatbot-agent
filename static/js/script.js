// ============================================
// ELF - Enhanced Learning Friend
// Advanced AI Chatbot Frontend
// ============================================

// DOM Elements
const chatBox = document.getElementById('chatBox');
const userInput = document.getElementById('userInput');
const sendBtn = document.getElementById('sendBtn');
const voiceBtn = document.getElementById('voiceBtn');
const ttsBtn = document.getElementById('ttsBtn');
const historyBtn = document.getElementById('historyBtn');
const statsBtn = document.getElementById('statsBtn');
const searchHistoryBtn = document.getElementById('searchHistoryBtn');
const summaryHistoryBtn = document.getElementById('summaryHistoryBtn');
const clearBtn = document.getElementById('clearBtn');
const themeBtn = document.getElementById('themeBtn');
const sentimentEmoji = document.getElementById('sentimentEmoji');
const sentimentTextEl = document.getElementById('sentimentText');
const sentimentFill = document.getElementById('sentimentFill');
const sentimentScore = document.getElementById('sentimentScore');
const typingIndicator = document.getElementById('typingIndicator');
const toastContainer = document.getElementById('toastContainer');
const searchInput = document.getElementById('searchInput');
const searchGoBtn = document.getElementById('searchGoBtn');
const searchResults = document.getElementById('searchResults');
const summaryUrlInput = document.getElementById('summaryUrlInput');
const summaryGoBtn = document.getElementById('summaryGoBtn');
const summaryResult = document.getElementById('summaryResult');
const modeIndicator = document.getElementById('modeIndicator');

let ttsEnabled = true;
let currentAudio = null;
let messageCount = 0;

// ============================================
// PARTICLES
// ============================================
function createParticles() {
    const particles = document.getElementById('particles');
    if (!particles) return;
    for (let i = 0; i < 50; i++) {
        const particle = document.createElement('div');
        particle.style.cssText = `
            position: absolute; width: 3px; height: 3px;
            background: rgba(255,255,255,0.5); border-radius: 50%;
            left: ${Math.random()*100}%; top: ${Math.random()*100}%;
            animation: float ${5+Math.random()*10}s infinite ease-in-out;
            animation-delay: ${Math.random()*5}s;
        `;
        particles.appendChild(particle);
    }
}

// ============================================
// TOAST NOTIFICATIONS
// ============================================
function showToast(message, type = 'info') {
    const toast = document.createElement('div');
    toast.className = `toast toast-${type}`;
    const icons = { success: '✅', error: '❌', info: 'ℹ️', warning: '⚠️' };
    toast.innerHTML = `${icons[type] || 'ℹ️'} ${message}`;
    toastContainer.appendChild(toast);
    setTimeout(() => {
        toast.style.animation = 'slideIn 0.3s ease-out reverse';
        setTimeout(() => toast.remove(), 300);
    }, 3000);
}

// ============================================
// RICH MESSAGE FORMATTING
// ============================================
function formatMessage(text) {
    // Escape HTML first (but keep our formatting)
    let html = text;
    
    // Bold: **text**
    html = html.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>');
    
    // URLs to clickable links
    html = html.replace(/(https?:\/\/[^\s<]+)/g, '<a href="$1" target="_blank" class="msg-link">$1</a>');
    
    // Newlines to <br>
    html = html.replace(/\n/g, '<br>');
    
    // Detect structured AI response sections and style them
    html = html.replace(/🔎\s*<strong>AI Answer:<\/strong>/g, '<div class="ai-section ai-answer-section"><div class="ai-section-header">🔎 AI Answer</div><div class="ai-section-body">');
    html = html.replace(/📌\s*<strong>Key Points:<\/strong>/g, '</div></div><div class="ai-section ai-keypoints-section"><div class="ai-section-header">📌 Key Points</div><div class="ai-section-body">');
    html = html.replace(/🌐\s*<strong>Sources:<\/strong>/g, '</div></div><div class="ai-section ai-sources-section"><div class="ai-section-header">🌐 Sources</div><div class="ai-section-body">');
    html = html.replace(/🧠\s*<strong>Insight:<\/strong>/g, '</div></div><div class="ai-section ai-insight-section"><div class="ai-section-header">🧠 Insight</div><div class="ai-section-body">');
    
    // Close any open sections at the end
    if (html.includes('ai-section-body')) {
        html += '</div></div>';
    }
    
    // Style bullet points
    html = html.replace(/•\s/g, '<span class="bullet">•</span> ');
    
    return html;
}

// ============================================
// MODE INDICATOR
// ============================================
function updateModeIndicator(mode) {
    if (!modeIndicator) return;
    const modes = {
        'WEB_SEARCH': { label: '🔎 AI Search Mode', cls: 'mode-search' },
        'SUMMARIZATION': { label: '📝 Summary Mode', cls: 'mode-summary' },
        'NORMAL': { label: '💬 Chat Mode', cls: 'mode-normal' }
    };
    const m = modes[mode] || modes['NORMAL'];
    modeIndicator.textContent = m.label;
    modeIndicator.className = `mode-indicator ${m.cls}`;
    modeIndicator.style.display = 'inline-flex';
}

// ============================================
// SEND MESSAGE
// ============================================
function sendMessage() {
    const message = userInput.value.trim();
    if (!message) return;

    addMessage(message, 'user');
    userInput.value = '';
    typingIndicator.style.display = 'flex';
    chatBox.scrollTop = chatBox.scrollHeight;

    fetch('/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ message: message })
    })
    .then(response => response.json())
    .then(data => {
        typingIndicator.style.display = 'none';
        
        if (data.response) {
            // Typewriter effect for bot
            addMessageTypewriter(data.response, 'bot');
            updateAnalysisPanel(data.analysis);
            updateSentimentIndicator(data.analysis.sentiment);
            updateModeIndicator(data.analysis.mode || 'NORMAL');
            
            if (ttsEnabled) {
                speakText(data.response);
            }
            
            messageCount++;
        }
    })
    .catch(error => {
        typingIndicator.style.display = 'none';
        addMessage('❌ Connection error. Please try again.', 'bot');
        showToast('Connection error. Please try again.', 'error');
    });
}

// ============================================
// ADD MESSAGE (instant)
// ============================================
function addMessage(text, sender) {
    const messageDiv = document.createElement('div');
    messageDiv.className = `message ${sender}-message`;
    
    const avatar = document.createElement('div');
    avatar.className = sender === 'bot' ? 'avatar bot-avatar' : 'avatar user-avatar';
    avatar.textContent = sender === 'bot' ? '🧝' : '👤';
    
    const contentDiv = document.createElement('div');
    contentDiv.className = 'message-content';
    
    const headerDiv = document.createElement('div');
    headerDiv.className = 'message-header';
    
    const nameSpan = document.createElement('strong');
    nameSpan.textContent = sender === 'bot' ? 'ELF' : 'You';
    
    const timeSpan = document.createElement('span');
    timeSpan.className = 'timestamp';
    timeSpan.textContent = new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
    
    headerDiv.appendChild(nameSpan);
    headerDiv.appendChild(timeSpan);
    
    const textDiv = document.createElement('div');
    textDiv.className = 'message-text';
    textDiv.innerHTML = formatMessage(text);
    
    contentDiv.appendChild(headerDiv);
    contentDiv.appendChild(textDiv);
    
    messageDiv.appendChild(avatar);
    messageDiv.appendChild(contentDiv);
    
    chatBox.appendChild(messageDiv);
    chatBox.scrollTop = chatBox.scrollHeight;
}

// ============================================
// ADD MESSAGE WITH TYPEWRITER EFFECT
// ============================================
function addMessageTypewriter(text, sender) {
    const messageDiv = document.createElement('div');
    messageDiv.className = `message ${sender}-message`;
    
    const avatar = document.createElement('div');
    avatar.className = 'avatar bot-avatar';
    avatar.textContent = '🧝';
    
    const contentDiv = document.createElement('div');
    contentDiv.className = 'message-content';
    
    const headerDiv = document.createElement('div');
    headerDiv.className = 'message-header';
    
    const nameSpan = document.createElement('strong');
    nameSpan.textContent = 'ELF';
    
    const timeSpan = document.createElement('span');
    timeSpan.className = 'timestamp';
    timeSpan.textContent = new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
    
    headerDiv.appendChild(nameSpan);
    headerDiv.appendChild(timeSpan);
    
    const textDiv = document.createElement('div');
    textDiv.className = 'message-text typewriter-active';
    
    contentDiv.appendChild(headerDiv);
    contentDiv.appendChild(textDiv);
    
    messageDiv.appendChild(avatar);
    messageDiv.appendChild(contentDiv);
    
    chatBox.appendChild(messageDiv);
    
    // Typewriter: reveal chunks fast for long AI answers
    const formattedHtml = formatMessage(text);
    const chunkSize = Math.max(3, Math.floor(text.length / 40));
    let i = 0;
    
    function typeChunk() {
        if (i < text.length) {
            const end = Math.min(i + chunkSize, text.length);
            const partial = text.substring(0, end);
            textDiv.innerHTML = formatMessage(partial);
            i = end;
            chatBox.scrollTop = chatBox.scrollHeight;
            requestAnimationFrame(() => setTimeout(typeChunk, 15));
        } else {
            textDiv.innerHTML = formattedHtml;
            textDiv.classList.remove('typewriter-active');
            chatBox.scrollTop = chatBox.scrollHeight;
        }
    }
    
    typeChunk();
}

// ============================================
// WEB SEARCH (sidebar)
// ============================================
function performWebSearch() {
    const query = searchInput.value.trim();
    if (!query) {
        showToast('Please enter a search query', 'warning');
        return;
    }

    searchResults.innerHTML = '<p class="search-loading">🔍 Searching & analyzing...</p>';

    fetch('/ai-search', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ query: query, num_results: 5 })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            displayAISearchResults(data);
            showToast(`Found ${data.count} results!`, 'success');
        } else {
            searchResults.innerHTML = '<p class="search-empty">No results found. Try different keywords.</p>';
            showToast('No results found', 'warning');
        }
    })
    .catch(error => {
        searchResults.innerHTML = '<p class="search-empty">Search failed. Check your connection.</p>';
        showToast('Search failed', 'error');
    });
}

function displayAISearchResults(data) {
    let html = '';
    
    if (data.answer) {
        html += `<div class="sidebar-ai-answer">
            <div class="sidebar-section-title">🔎 AI Answer</div>
            <p>${data.answer.substring(0, 300)}${data.answer.length > 300 ? '...' : ''}</p>
        </div>`;
    }
    
    if (data.key_points && data.key_points.length > 0) {
        html += '<div class="sidebar-key-points"><div class="sidebar-section-title">📌 Key Points</div><ul>';
        data.key_points.forEach(point => {
            html += `<li>${point.substring(0, 150)}</li>`;
        });
        html += '</ul></div>';
    }
    
    if (data.sources && data.sources.length > 0) {
        html += '<div class="sidebar-sources"><div class="sidebar-section-title">🌐 Sources</div>';
        data.sources.forEach((src, i) => {
            html += `<div class="source-item">
                <a href="${src.url}" target="_blank">${i+1}. ${src.title}</a>
                <span class="source-domain">${src.domain || ''}</span>
            </div>`;
        });
        html += '</div>';
    }
    
    searchResults.innerHTML = html;
}

// ============================================
// SUMMARIZATION (sidebar)
// ============================================
function performSummarization() {
    const input = summaryUrlInput.value.trim();
    if (!input) {
        showToast('Please enter text or URL to summarize', 'warning');
        return;
    }

    const method = document.querySelector('input[name="summaryMethod"]:checked').value;
    const numSentences = parseInt(document.getElementById('summaryLength').value);

    summaryResult.innerHTML = '<p class="search-loading">📝 Generating summary...</p>';

    const isUrl = input.startsWith('http://') || input.startsWith('https://');

    fetch('/summarize', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
            url: isUrl ? input : '',
            text: isUrl ? '' : input,
            num_sentences: numSentences,
            method: method
        })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            displaySummary(data);
            showToast('Summary ready!', 'success');
        } else {
            summaryResult.innerHTML = `<p class="search-empty">Error: ${data.error}</p>`;
            showToast('Summarization failed', 'error');
        }
    })
    .catch(error => {
        summaryResult.innerHTML = '<p class="search-empty">Summarization failed</p>';
        showToast('Error: ' + error, 'error');
    });
}

function displaySummary(data) {
    let html = '';
    if (data.title) {
        html += `<div class="sidebar-section-title">📄 ${data.title}</div>`;
    }
    html += `<div class="sidebar-ai-answer"><p>${data.summary}</p></div>`;
    html += `<div class="summary-meta">
        <span>Method: ${data.method}</span>
        <span>Compression: ${(data.compression_ratio * 100).toFixed(0)}%</span>
    </div>`;
    summaryResult.innerHTML = html;
}

// ============================================
// ANALYSIS PANEL
// ============================================
function updateAnalysisPanel(analysis) {
    if (!analysis) return;
    
    const sentText = analysis.sentiment ? analysis.sentiment.toUpperCase() : '-';
    document.getElementById('analysisSentiment').textContent = sentText;
    
    const entities = analysis.entities && analysis.entities.length > 0 
        ? analysis.entities.map(e => e.text).join(', ') 
        : 'None detected';
    document.getElementById('analysisEntities').textContent = entities;
    
    const intents = analysis.intents && analysis.intents.length > 0 
        ? analysis.intents.join(', ') 
        : 'general';
    document.getElementById('analysisIntent').textContent = intents;
    
    const keywords = analysis.keywords && analysis.keywords.length > 0 
        ? analysis.keywords.join(', ') 
        : 'None';
    document.getElementById('analysisKeywords').textContent = keywords;
}

// ============================================
// SENTIMENT INDICATOR
// ============================================
function updateSentimentIndicator(sentiment) {
    const sentiments = {
        'positive': { emoji: '😊', text: 'Positive Vibes', color: '#4ade80', score: 0.8 },
        'negative': { emoji: '😞', text: 'Needs Support', color: '#f87171', score: 0.3 },
        'neutral': { emoji: '😐', text: 'Neutral Mood', color: '#fbbf24', score: 0.5 }
    };
    
    const data = sentiments[sentiment] || sentiments['neutral'];
    sentimentEmoji.textContent = data.emoji;
    sentimentTextEl.textContent = data.text;
    sentimentFill.style.width = (data.score * 100) + '%';
    sentimentFill.style.background = `linear-gradient(90deg, ${data.color}, ${data.color}dd)`;
    sentimentScore.textContent = data.score.toFixed(1);
}

// ============================================
// TEXT-TO-SPEECH
// ============================================
function speakText(text) {
    if (currentAudio) {
        currentAudio.pause();
        currentAudio = null;
    }
    
    const cleanText = text.replace(/[\u{1F300}-\u{1F9FF}]/gu, '')
                         .replace(/\*\*/g, '')
                         .substring(0, 200);
    
    fetch('/text-to-speech', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ text: cleanText })
    })
    .then(response => response.blob())
    .then(blob => {
        const audioUrl = URL.createObjectURL(blob);
        currentAudio = new Audio(audioUrl);
        currentAudio.play();
    })
    .catch(error => console.log('TTS Error:', error));
}

// ============================================
// VOICE RECOGNITION
// ============================================
function startVoiceRecognition() {
    if (!('webkitSpeechRecognition' in window) && !('SpeechRecognition' in window)) {
        showToast('Voice recognition not supported. Use Chrome browser.', 'error');
        return;
    }

    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    const recognition = new SpeechRecognition();
    recognition.continuous = false;
    recognition.interimResults = false;
    recognition.lang = 'en-US';

    voiceBtn.classList.add('recording');
    showToast('Listening... Speak now! 🎤', 'info');

    recognition.onresult = function(event) {
        const transcript = event.results[0][0].transcript;
        userInput.value = transcript;
        voiceBtn.classList.remove('recording');
        showToast('Voice captured!', 'success');
        sendMessage();
    };

    recognition.onerror = function(event) {
        voiceBtn.classList.remove('recording');
        showToast('Voice error: ' + event.error, 'error');
    };

    recognition.onend = function() {
        voiceBtn.classList.remove('recording');
    };

    recognition.start();
}

// ============================================
// UTILITY FUNCTIONS
// ============================================
function toggleTTS() {
    ttsEnabled = !ttsEnabled;
    ttsBtn.classList.toggle('active', ttsEnabled);
    showToast(ttsEnabled ? 'Voice output enabled 🔊' : 'Voice output disabled 🔇', 'info');
}

function viewHistory() {
    fetch('/history?limit=10')
    .then(r => r.json())
    .then(data => {
        if (data.history && data.history.length > 0) {
            chatBox.innerHTML = '';
            data.history.reverse().forEach(item => {
                addMessage(item.user_message, 'user');
                addMessage(item.bot_response, 'bot');
            });
            showToast('History loaded', 'success');
        } else {
            showToast('No conversation history found.', 'warning');
        }
    })
    .catch(() => showToast('Error loading history.', 'error'));
}

function viewSentimentStats() {
    fetch('/sentiment-stats')
    .then(r => r.json())
    .then(data => {
        if (data.stats && data.stats.length > 0) {
            let msg = '📊 **Sentiment Statistics:**\n\n';
            data.stats.forEach(stat => {
                const emoji = stat.sentiment === 'positive' ? '😊' : stat.sentiment === 'negative' ? '😞' : '😐';
                msg += `${emoji} ${stat.sentiment.toUpperCase()}: ${stat.count} messages (Score: ${stat.avg_score ? stat.avg_score.toFixed(2) : 'N/A'})\n`;
            });
            addMessage(msg, 'bot');
        } else {
            showToast('No sentiment data yet.', 'info');
        }
    })
    .catch(() => showToast('Error loading stats.', 'error'));
}

function viewSearchHistory() {
    fetch('/search-history?limit=10')
    .then(r => r.json())
    .then(data => {
        if (data.searches && data.searches.length > 0) {
            let msg = '🔍 **Recent Searches:**\n\n';
            data.searches.forEach((s, i) => {
                msg += `${i+1}. "${s.query}" (${s.num_results} results)\n`;
            });
            addMessage(msg, 'bot');
        } else {
            showToast('No search history yet', 'info');
        }
    })
    .catch(() => showToast('Error loading search history', 'error'));
}

function viewSummaryHistory() {
    fetch('/summary-history?limit=10')
    .then(r => r.json())
    .then(data => {
        if (data.summaries && data.summaries.length > 0) {
            let msg = '📝 **Recent Summaries:**\n\n';
            data.summaries.forEach((s, i) => {
                msg += `${i+1}. ${s.url || 'Text'} (${s.method})\n`;
            });
            addMessage(msg, 'bot');
        } else {
            showToast('No summary history yet', 'info');
        }
    })
    .catch(() => showToast('Error loading summary history', 'error'));
}

function clearChat() {
    chatBox.innerHTML = '';
    messageCount = 0;
    showToast('Chat cleared!', 'success');
    addMessage("Chat cleared! 🧹 I'm ELF, and I'm still here. Ask me any question — I'll search the web, analyze sources, and give you a structured AI answer! 🚀", 'bot');
}

function toggleTheme() {
    document.body.classList.toggle('light-theme');
    showToast('Theme toggled!', 'info');
}

// ============================================
// EVENT LISTENERS
// ============================================
sendBtn.addEventListener('click', sendMessage);
userInput.addEventListener('keypress', (e) => { if (e.key === 'Enter') sendMessage(); });
voiceBtn.addEventListener('click', startVoiceRecognition);
ttsBtn.addEventListener('click', toggleTTS);
historyBtn.addEventListener('click', viewHistory);
statsBtn.addEventListener('click', viewSentimentStats);
searchHistoryBtn.addEventListener('click', viewSearchHistory);
summaryHistoryBtn.addEventListener('click', viewSummaryHistory);
clearBtn.addEventListener('click', clearChat);
themeBtn.addEventListener('click', toggleTheme);
searchGoBtn.addEventListener('click', performWebSearch);
searchInput.addEventListener('keypress', (e) => { if (e.key === 'Enter') performWebSearch(); });
summaryGoBtn.addEventListener('click', performSummarization);

// Quick action chips
document.addEventListener('click', function(e) {
    if (e.target.classList.contains('chip')) {
        userInput.value = e.target.getAttribute('data-action');
        sendMessage();
    }
});

// Feature card interactions
document.querySelectorAll('.feature-card').forEach(card => {
    card.addEventListener('click', function() {
        const feature = this.getAttribute('data-feature');
        const messages = {
            'nlp': 'Tell me about your NLP capabilities',
            'sentiment': 'Analyze my mood: I\'m feeling great!',
            'search': 'What is artificial intelligence?',
            'summary': 'How does your summarization work?',
            'weather': 'What\'s the weather in London?',
            'news': 'Show me technology news',
            'voice': 'Tell me about your voice features',
            'math': 'Calculate 15 * 23 + 100'
        };
        userInput.value = messages[feature] || '';
        sendMessage();
    });
});

// Toggle analysis panel
const toggleAnalysis = document.getElementById('toggleAnalysis');
if (toggleAnalysis) {
    toggleAnalysis.addEventListener('click', function() {
        const grid = document.querySelector('.analysis-grid');
        const panels = document.querySelectorAll('.quick-actions, .search-panel, .summary-panel');
        const isHidden = grid.style.display === 'none';
        grid.style.display = isHidden ? '' : 'none';
        panels.forEach(p => p.style.display = isHidden ? '' : 'none');
        this.textContent = isHidden ? '−' : '+';
    });
}

// ============================================
// INITIALIZE
// ============================================
window.addEventListener('load', () => {
    console.log('🧝 ELF (Enhanced Learning Friend) is online!');
    console.log('✨ AI Search | Summarization | NLP | Sentiment | Voice I/O');
    
    createParticles();
    showToast("Hey there! I'm ELF, your AI search assistant! 🧝", 'success');
    
    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.style.animation = 'fadeIn 0.6s ease-out';
            }
        });
    });
    
    document.querySelectorAll('.feature-card').forEach(card => observer.observe(card));
});