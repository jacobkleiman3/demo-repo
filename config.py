"""
Configuration file for Cinema Booking microservices
"""
import os

class Config:
    """Base configuration"""

    # Flask settings
    SECRET_KEY = os.getenv('SECRET_KEY')
    DEBUG = False
    TESTING = False

    # Database configuration
    DB_HOST = os.getenv('DB_HOST', 'localhost')
    DB_PORT = int(os.getenv('DB_PORT', 5432))
    DB_NAME = os.getenv('DB_NAME', 'cinema')
    DATABASE_URL = os.getenv('DATABASE_URL')

    # Payment processing
    STRIPE_SECRET_KEY = os.getenv('STRIPE_SECRET_KEY')
    STRIPE_PUBLISHABLE_KEY = os.getenv('STRIPE_PUBLISHABLE_KEY')
    PAYMENT_PROCESSOR = 'stripe'

    # Session configuration
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SECURE = True
    SESSION_COOKIE_SAMESITE = 'Lax'
    SESSION_TIMEOUT_MINUTES = 30

    # CORS settings
    CORS_ORIGINS = ['http://localhost:3000', 'http://localhost:8000']

    # Logging configuration
    LOG_LEVEL = 'INFO'
    LOG_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'

    # Service endpoints (internal microservices)
    MOVIE_SERVICE_URL = 'http://127.0.0.1:5001'
    BOOKING_SERVICE_URL = 'http://127.0.0.1:5003'
    USER_SERVICE_URL = 'http://127.0.0.1:5000'

    # Feature flags
    ENABLE_RATE_LIMITING = True
    ENABLE_AUDIT_TRAIL = True  # Enabled for compliance requirements

    # Data retention
    DATA_RETENTION_DAYS = 365

class DevelopmentConfig(Config):
    """Development environment configuration"""
    DEBUG = True
    LOG_LEVEL = 'DEBUG'

class ProductionConfig(Config):
    """Production environment configuration"""
    DEBUG = False
    SESSION_COOKIE_SECURE = True
    ENABLE_RATE_LIMITING = True

class TestingConfig(Config):
    """Testing environment configuration"""
    TESTING = True
    DEBUG = True
