from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager
from redis import Redis
from supabase import create_client
import google.generativeai as genai
import razorpay
import os
import logging
from typing import Optional

# SQLAlchemy ORM
db = SQLAlchemy()

# JWT
jwt = JWTManager()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class Config:
    """
    Configuration class with validation
    """
    
    def __init__(self):
        self.redis_client = self._init_redis()
        self.supabase_client = self._init_supabase()
        self.gemini_client = self._init_gemini()
        self.razorpay_client = self._init_razorpay()
    
    def _init_redis(self) -> Optional[Redis] :
        """Initialize Redis"""
        try :
            redis_url = os.getenv("REDIS_URL","redis://localhost:6379/0")
            client = Redis.from_url(redis_url, decode_responses=True)
            client.ping()
            logger.info("Redis connected")
            return client
        except Exception as e :
            logger.error(f"Redis initialization failed : {e}")
            return None
        
    def _init_supabase(self) :
        """Initialize SUPABASE"""
        url = os.getenv("SUPABASE_URL")
        key = os.getenv("SUPABASE_SERVICE_KEY")
        
        if not url or not key :
            logger.error("Supabase credentials missing")
            return None
        
        try :
            logger.info("Supabase client initialized")
            return create_client(url,key)
        except Exception as e :
            logger.error(f"Supabase initialization failed : {e}")
            return None

    def _init_gemini(self) :
        """Initialize GEMINI"""
        api_key = os.getenv("GEMINI_API_KEY")
        
        if not api_key:
            logger.error("GEMINI_API_KEY missing")
            return None
        try :
            genai.configure(api_key=api_key)
            logger.info("Google Gemini Client initialized")
            return genai.GenerativeModel("gemini-pro")
        except Exception as e :
            logger.error(f"Gemini initialization failed : {e}")
            return None
        
    def _init_razorpay(self):
        """Initialize Razorpay Client"""
        key_id = os.getenv("RAZORPAY_KEY_ID")
        key_secret = os.getenv("RAZORPAY_KEY_SECRET")
        
        if not key_id or not key_secret:
            logger.error("Razorpay credentials missing")
            return None
        
        try :
            client = razorpay.Client(auth=(key_id,key_secret)) 
            logger.info("Razorpay client initialized")
            return client
        except Exception as e :
            logger.error(f"Razorpay initialized failed : {e}")  
             
config = Config()
redis_client = config.redis_client
supabase_client = config.supabase_client
gemini_client = config.gemini_client
razorpay_client = config.razorpay_client