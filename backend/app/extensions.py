from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager
from redis import Redis
from supabase import create_client
import google.generativeai as genai
import os
from typing import Optional

# SQLAlchemy ORM
db = SQLAlchemy()

# JWT
jwt = JWTManager()

class Config:
    """
    Configuration class with validation
    """
    
    def __init__(self):
        self.redis_client = self._init_redis()
        self.supabase_client = self._init_supabase()
        self.gemini_client = self._init_gemini()
    
    def _init_redis(self) -> Optional[Redis] :
        """Initialize Redis"""
        try :
            redis_url = os.getenv("REDIS_URL","redis://localhost:6379/0")
            client = Redis.from_url(redis_url, decode_responses=True)
            client.ping()
            return client
        except Exception as e :
            print(f"Redis initialization failed : {e}")
            return None
        
    def _init_supabase(self) :
        """Initialize SUPABASE"""
        url = os.getenv("SUPABASE_URL")
        key = os.getenv("SUPABASE_SERVICE_KEY")
        
        if not url or not key :
            print("Supabase credentials missing")
            return None
        
        try :
            return create_client(url,key)
        except Exception as e :
            print(f"Supabase initialization failed : {e}")
            return None

    def _init_gemini(self) :
        """Initialize GEMINI"""
        api_key = os.getenv("GEMINI_API_KEY")
        
        if not api_key:
            print("GEMINI_API_KEY missing")
            return None
        try :
            genai.configure(api_key=api_key)
            return genai.GenerativeModel("gemini-pro")
        except Exception as e :
            print(f"Gemini initialization failed : {e}")
            return None
        
config = Config()
redis_client = config.redis_client
supabase_client = config.supabase_client
gemini_client = config.gemini_client