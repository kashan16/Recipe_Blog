from flask import Flask
from .config import Config
from .extensions import db, jwt, redit_client
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
        
    return app    