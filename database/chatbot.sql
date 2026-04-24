CREATE DATABASE IF NOT EXISTS chatbot_db;
USE chatbot_db;

-- Conversation History Table
CREATE TABLE IF NOT EXISTS conversations (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_message TEXT NOT NULL,
    bot_response TEXT NOT NULL,
    sentiment VARCHAR(20),
    sentiment_score FLOAT,
    entities TEXT,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- User Sessions Table
CREATE TABLE IF NOT EXISTS sessions (
    id INT AUTO_INCREMENT PRIMARY KEY,
    session_id VARCHAR(100) UNIQUE NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_active TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

-- Web Search History
CREATE TABLE IF NOT EXISTS search_history (
    id INT AUTO_INCREMENT PRIMARY KEY,
    query TEXT NOT NULL,
    results TEXT,
    num_results INT,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Sentiment Analytics
CREATE TABLE IF NOT EXISTS sentiment_analytics (
    id INT AUTO_INCREMENT PRIMARY KEY,
    message TEXT NOT NULL,
    sentiment VARCHAR(20) NOT NULL,
    compound_score FLOAT,
    positive_score FLOAT,
    neutral_score FLOAT,
    negative_score FLOAT,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Text Summaries
CREATE TABLE IF NOT EXISTS text_summaries (
    id INT AUTO_INCREMENT PRIMARY KEY,
    original_text TEXT NOT NULL,
    summary TEXT NOT NULL,
    url VARCHAR(500),
    method VARCHAR(50),
    compression_ratio FLOAT,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);