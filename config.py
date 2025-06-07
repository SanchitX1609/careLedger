import os
from datetime import timedelta
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Get absolute path to project directory
basedir = os.path.abspath(os.path.dirname(__file__))

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production'
    #SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or f'sqlite:///{os.path.join(basedir, "instance", "careledger.db")}'
    SQLALCHEMY_DATABASE_URI = 'sqlite:////workspaces/AidTransparency-website/careLedger/instance/careledger.db'  # Hardcoded for testing
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Security Configuration
    WTF_CSRF_ENABLED = os.environ.get('WTF_CSRF_ENABLED', 'True').lower() == 'true'
    WTF_CSRF_TIME_LIMIT = 3600  # 1 hour
    WTF_CSRF_SSL_STRICT = False  # Disable SSL strict for development
    SESSION_COOKIE_SECURE = os.environ.get('SESSION_COOKIE_SECURE', 'False').lower() == 'true'
    SESSION_COOKIE_HTTPONLY = os.environ.get('SESSION_COOKIE_HTTPONLY', 'True').lower() == 'true'
    SESSION_COOKIE_SAMESITE = 'Lax'  # Allow cross-origin for development
    PERMANENT_SESSION_LIFETIME = timedelta(hours=1)
    
    # Cache Configuration
    CACHE_TYPE = os.environ.get('CACHE_TYPE', 'SimpleCache')
    CACHE_DEFAULT_TIMEOUT = int(os.environ.get('CACHE_DEFAULT_TIMEOUT', '300'))
    CACHE_REDIS_URL = os.environ.get('REDIS_URL', 'redis://localhost:6379/0')
    
    # App Configuration
    ITEMS_PER_PAGE = 20
    LOW_STOCK_THRESHOLD = 0.2  # 20% of minimum level
    
    # AI Forecasting Configuration
    FORECAST_DAYS = 7
    MIN_DATA_POINTS = 5  # Minimum data points needed for forecasting
    
    # Alert Configuration
    ALERT_CHECK_INTERVAL = timedelta(hours=6)
    EMAIL_ALERTS = os.environ.get('EMAIL_ALERTS', 'False').lower() == 'true'
    
class DevelopmentConfig(Config):
    DEBUG = True
    
class ProductionConfig(Config):
    DEBUG = False
    
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}
