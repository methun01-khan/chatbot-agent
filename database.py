import sqlite3
import mysql.connector
from mysql.connector import Error
import json
import os
from config import DB_CONFIG

class Database:
    def __init__(self):
        self.connection = None
        
        # Check if Railway MySQL environment variables exist
        self.use_mysql = bool(os.getenv('MYSQL_URL') or os.getenv('MYSQLHOST') or (DB_CONFIG.get('host') and DB_CONFIG.get('host') != 'localhost'))
        
        if os.getenv('MYSQL_URL') or os.getenv('MYSQLHOST'):
            self.db_type = 'mysql'
            self.mysql_config = {
                'host': os.getenv('MYSQLHOST', DB_CONFIG.get('host', 'localhost')),
                'user': os.getenv('MYSQLUSER', DB_CONFIG.get('user', 'root')),
                'password': os.getenv('MYSQLPASSWORD', DB_CONFIG.get('password', '')),
                'database': os.getenv('MYSQLDATABASE', DB_CONFIG.get('database', 'chatbot_db')),
                'port': int(os.getenv('MYSQLPORT', 3306))
            }
        elif DB_CONFIG.get('host') and DB_CONFIG.get('host') != 'localhost' and DB_CONFIG.get('password'):
            self.db_type = 'mysql'
            self.mysql_config = DB_CONFIG
        else:
            self.db_type = 'sqlite'
            self.db_path = 'chatbot.db'
            
        self.connect()
        self.init_tables()
    
    def connect(self):
        try:
            if self.db_type == 'mysql':
                self.connection = mysql.connector.connect(**self.mysql_config)
                print("✅ MySQL Database connected successfully!")
            else:
                self.connection = sqlite3.connect(self.db_path, check_same_thread=False)
                self.connection.row_factory = sqlite3.Row
                print("✅ SQLite Database connected successfully!")
        except Exception as err:
            print(f"❌ Database connection error: {err}")
            # Fallback to SQLite
            if self.db_type == 'mysql':
                print("⚠️ Falling back to SQLite...")
                self.db_type = 'sqlite'
                self.db_path = 'chatbot.db'
                self.connect()
    
    def get_cursor(self):
        if self.db_type == 'mysql':
            if not self.connection.is_connected():
                self.connect()
            return self.connection.cursor(dictionary=True)
        else:
            return self.connection.cursor()
            
    def get_placeholder(self):
        return "%s" if self.db_type == 'mysql' else "?"
        
    def init_tables(self):
        try:
            cursor = self.get_cursor()
            
            auto_inc = "AUTO_INCREMENT" if self.db_type == 'mysql' else "AUTOINCREMENT"
            int_pk = "INT" if self.db_type == 'mysql' else "INTEGER"
            
            # Conversations table
            cursor.execute(f'''CREATE TABLE IF NOT EXISTS conversations (
                id {int_pk} PRIMARY KEY {auto_inc},
                user_message TEXT NOT NULL,
                bot_response TEXT NOT NULL,
                sentiment VARCHAR(20),
                sentiment_score FLOAT,
                entities TEXT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
            )''')
            
            # Search history table
            cursor.execute(f'''CREATE TABLE IF NOT EXISTS search_history (
                id {int_pk} PRIMARY KEY {auto_inc},
                query TEXT NOT NULL,
                results TEXT,
                num_results INTEGER,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
            )''')
            
            # Sentiment analytics table
            cursor.execute(f'''CREATE TABLE IF NOT EXISTS sentiment_analytics (
                id {int_pk} PRIMARY KEY {auto_inc},
                message TEXT NOT NULL,
                sentiment VARCHAR(20) NOT NULL,
                compound_score FLOAT,
                positive_score FLOAT,
                neutral_score FLOAT,
                negative_score FLOAT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
            )''')
            
            # Text summaries table
            cursor.execute(f'''CREATE TABLE IF NOT EXISTS text_summaries (
                id {int_pk} PRIMARY KEY {auto_inc},
                original_text TEXT NOT NULL,
                summary TEXT NOT NULL,
                url VARCHAR(500),
                method VARCHAR(50),
                compression_ratio FLOAT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
            )''')
            
            self.connection.commit()
            cursor.close()
        except Exception as e:
            print(f"Error initializing tables: {e}")
    
    def save_conversation(self, user_message, bot_response, sentiment=None, sentiment_score=None, entities=None):
        try:
            cursor = self.get_cursor()
            entities_json = json.dumps(entities) if entities else None
            p = self.get_placeholder()
            query = f"""INSERT INTO conversations 
                      (user_message, bot_response, sentiment, sentiment_score, entities) 
                      VALUES ({p}, {p}, {p}, {p}, {p})"""
            cursor.execute(query, (user_message, bot_response, sentiment, sentiment_score, entities_json))
            self.connection.commit()
            cursor.close()
            return True
        except Exception as e:
            print(f"Error saving conversation: {e}")
            return False
    
    def save_search_history(self, query, results, num_results=0):
        try:
            cursor = self.get_cursor()
            results_json = json.dumps(results) if results else None
            p = self.get_placeholder()
            query_sql = f"""INSERT INTO search_history (query, results, num_results) 
                          VALUES ({p}, {p}, {p})"""
            cursor.execute(query_sql, (query, results_json, num_results))
            self.connection.commit()
            cursor.close()
            return True
        except Exception as e:
            print(f"Error saving search: {e}")
            return False
    
    def save_summary(self, original_text, summary, url=None, method='extractive', compression_ratio=0.0):
        try:
            cursor = self.get_cursor()
            p = self.get_placeholder()
            query = f"""INSERT INTO text_summaries 
                      (original_text, summary, url, method, compression_ratio) 
                      VALUES ({p}, {p}, {p}, {p}, {p})"""
            cursor.execute(query, (original_text[:5000], summary, url, method, compression_ratio))
            self.connection.commit()
            cursor.close()
            return True
        except Exception as e:
            print(f"Error saving summary: {e}")
            return False
    
    def get_recent_searches(self, limit=10):
        try:
            cursor = self.get_cursor()
            query = f"SELECT * FROM search_history ORDER BY timestamp DESC LIMIT {int(limit)}"
            cursor.execute(query)
            results = [dict(row) for row in cursor.fetchall()]
            cursor.close()
            return results
        except Exception as e:
            print(f"Error fetching searches: {e}")
            return []
    
    def get_recent_summaries(self, limit=10):
        try:
            cursor = self.get_cursor()
            query = f"SELECT * FROM text_summaries ORDER BY timestamp DESC LIMIT {int(limit)}"
            cursor.execute(query)
            results = [dict(row) for row in cursor.fetchall()]
            cursor.close()
            return results
        except Exception as e:
            print(f"Error fetching summaries: {e}")
            return []
    
    def save_sentiment_analytics(self, message, sentiment_data):
        try:
            cursor = self.get_cursor()
            p = self.get_placeholder()
            query = f"""INSERT INTO sentiment_analytics 
                      (message, sentiment, compound_score, positive_score, neutral_score, negative_score) 
                      VALUES ({p}, {p}, {p}, {p}, {p}, {p})"""
            cursor.execute(query, (
                message, 
                sentiment_data['sentiment'],
                sentiment_data['compound'],
                sentiment_data['positive'],
                sentiment_data['neutral'],
                sentiment_data['negative']
            ))
            self.connection.commit()
            cursor.close()
            return True
        except Exception as e:
            print(f"Error saving sentiment: {e}")
            return False
    
    def get_conversation_history(self, limit=10):
        try:
            cursor = self.get_cursor()
            query = f"SELECT * FROM conversations ORDER BY timestamp DESC LIMIT {int(limit)}"
            cursor.execute(query)
            results = [dict(row) for row in cursor.fetchall()]
            cursor.close()
            return results
        except Exception as e:
            print(f"Error fetching history: {e}")
            return []
    
    def get_sentiment_stats(self):
        try:
            cursor = self.get_cursor()
            query = """SELECT 
                        sentiment, 
                        COUNT(*) as count,
                        AVG(compound_score) as avg_score
                      FROM sentiment_analytics 
                      GROUP BY sentiment"""
            cursor.execute(query)
            results = [dict(row) for row in cursor.fetchall()]
            cursor.close()
            return results
        except Exception as e:
            print(f"Error fetching sentiment stats: {e}")
            return []
    
    def close(self):
        if self.connection:
            self.connection.close()