import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret-key")
    
    # Supabase Postgres URL (from Supabase Project Settings > Database > Connection String)
    SQLALCHEMY_DATABASE_URI = os.getenv("SUPABASE_DB_URL")
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # JWT for our backend auth
    JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "jwt-secret-key")

    # Supabase service keys
    SUPABASE_URL = os.getenv("SUPABASE_URL")
    SUPABASE_SERVICE_KEY = os.getenv("SUPABASE_SERVICE_KEY")

    # Redis (for caching AI responses)
    REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")

    # API Keys
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
    STRIPE_API_KEY = os.getenv("STRIPE_API_KEY", "")

class DevelopmentConfig(Config):
    DEBUG = True

class ProductionConfig(Config):
    DEBUG = False

class TestingConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"
