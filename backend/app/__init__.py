from flask import Flask
from .config import Config
from .extensions import db, jwt, redis_client, supabase_client, gemini_client
from .routes import register_routes

def create_app(config_class=Config):
    """
    Flask application factory pattern.
    Allows creating multiple instances with different configs
    """
    
    app = Flask(__name__)
    
    app.config.from_object(config_class)
    
    db.init_app(app)
    jwt.init_app(app)
    
    register_routes(app)
    
    @app.route("/health",methods=["GET"])
    def health():
        return {"status":"ok"}, 200
    
    with app.app_context():
        test_connections()
        
    return app

def test_connections():
    """Test all external services"""
    print("Testing")
    
    if redis_client:
        try : 
            redis_client.ping()
            print("Redis connected")
        except :
            print("Redis connection failed")
    if supabase_client:
        print("Supabase available")
    else :
        print("Supabase not available")
        
    if gemini_client:
        print("Gemini available")
    else :
        print("Gemini not available")