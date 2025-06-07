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
    
    # Enhanced UI settings
    ENABLE_PWA = os.environ.get('ENABLE_PWA', 'true').lower() == 'true'
    ENABLE_REAL_TIME_UPDATES = os.environ.get('ENABLE_REAL_TIME_UPDATES', 'true').lower() == 'true'
    ENABLE_MOBILE_OPTIMIZATIONS = os.environ.get('ENABLE_MOBILE_OPTIMIZATIONS', 'true').lower() == 'true'


    # Security Configuration
    WTF_CSRF_ENABLED = os.environ.get('WTF_CSRF_ENABLED', 'True').lower() == 'true'
    WTF_CSRF_TIME_LIMIT = 3600  # 1 hour
    WTF_CSRF_SSL_STRICT = False  # Disable SSL strict for development
    # SESSION_COOKIE_SECURE = os.environ.get('SESSION_COOKIE_SECURE', 'False').lower() == 'true'
    # SESSION_COOKIE_HTTPONLY = os.environ.get('SESSION_COOKIE_HTTPONLY', 'True').lower() == 'true'
    # SESSION_COOKIE_SAMESITE = 'Lax'  # Allow cross-origin for development
    # PERMANENT_SESSION_LIFETIME = timedelta(hours=1)

    WTF_CSRF_CHECK_DEFAULT = False  # Disable CSRF for development
    SESSION_COOKIE_SECURE = False  # Disable for development
    SESSION_COOKIE_HTTPONLY = False  # Disable for development
    SESSION_COOKIE_SAMESITE = None  # More permissive for development
    PERMANENT_SESSION_LIFETIME = timedelta(hours=24)  # Extended for development
    
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
    # Cache settings
    CACHE_TYPE = os.environ.get('CACHE_TYPE', 'simple')
    CACHE_REDIS_URL = os.environ.get('CACHE_REDIS_URL')
    CACHE_DEFAULT_TIMEOUT = 300
    
    # Compression
    COMPRESS_MIMETYPES = [
        'text/html', 'text/css', 'text/xml', 'application/json',
        'application/javascript', 'text/javascript'
    ]
    COMPRESS_LEVEL = 6
    COMPRESS_MIN_SIZE = 500


class DevelopmentConfig(Config):
    DEBUG = True
    WTF_CSRF_ENABLED = False  # Disable CSRF for development
    WTF_CSRF_CHECK_DEFAULT = False
    
class ProductionConfig(Config):
    DEBUG = False
    
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}
