import os

# Database Configuration
DB_CONFIG = {
    'host': os.getenv('MYSQLHOST', 'localhost'),
    'user': os.getenv('MYSQLUSER', 'root'),
    'password': os.getenv('MYSQLPASSWORD', ''),
    'database': os.getenv('MYSQLDATABASE', 'chatbot_db'),
    'port': int(os.getenv('MYSQLPORT', 3306))
}

# Flask Configuration
FLASK_CONFIG = {
    'host': '0.0.0.0',
    'port': int(os.getenv('PORT', 5000)),
    'debug': os.getenv('FLASK_DEBUG', 'true').lower() == 'true'
}

# API Keys (set via environment variables)
API_KEYS = {
    'openweathermap': os.getenv('OPENWEATHERMAP_API_KEY', ''),
    'newsapi': os.getenv('NEWSAPI_KEY', '')
}

# Chatbot Configuration
CHATBOT_NAME = "ELF"
DEFAULT_LOCATION = "Dhaka"  # Default city for weather

# NLP Configuration
NLP_CONFIG = {
    'min_confidence': 0.5,
    'max_entities': 10
}