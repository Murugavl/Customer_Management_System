import os
from datetime import timedelta
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class Config:
    """Application configuration class"""
    
    # Flask Configuration
    SECRET_KEY = os.getenv("SECRET_KEY")
    if not SECRET_KEY:
        raise RuntimeError("SECRET_KEY is not set in environment variables")
    
    # MongoDB Configuration
    MONGO_URI = os.getenv("MONGO_URI")
    if not MONGO_URI:
        raise RuntimeError("MONGO_URI is not set in environment variables")
    
    # Session Configuration
    SESSION_COOKIE_SECURE = True  # HTTPS only (set to False for local development)
    SESSION_COOKIE_HTTPONLY = True  # Prevent JavaScript access
    SESSION_COOKIE_SAMESITE = 'Lax'  # CSRF protection
    PERMANENT_SESSION_LIFETIME = timedelta(hours=2)  # Session timeout
    
    # Application Settings
    DEBUG = os.getenv("FLASK_DEBUG", "False").lower() == "true"
    TESTING = False
    
    # Pagination
    CUSTOMERS_PER_PAGE = 20
    
    # Database Settings
    DB_NAME = "customer_management"
    COLLECTION_NAME = "customer"
    
    # User Credentials (temporary - will move to database later)
    USER_NAME = os.getenv("USER_NAME")
    # Preferred: store only the hash — generate with:
    #   python -c "from werkzeug.security import generate_password_hash; print(generate_password_hash('your_password'))"
    # then set USER_PASSWORD_HASH in .env and remove USER_PASSWORD entirely.
    USER_PASSWORD_HASH = os.getenv("USER_PASSWORD_HASH")   # preferred
    USER_PASSWORD = os.getenv("USER_PASSWORD")             # legacy fallback


class DevelopmentConfig(Config):
    """Development configuration"""
    DEBUG = True
    SESSION_COOKIE_SECURE = False  # Allow HTTP in development


class ProductionConfig(Config):
    """Production configuration"""
    DEBUG = False
    SESSION_COOKIE_SECURE = True


class TestingConfig(Config):
    """Testing configuration"""
    TESTING = True
    SESSION_COOKIE_SECURE = False


# Configuration dictionary
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}
