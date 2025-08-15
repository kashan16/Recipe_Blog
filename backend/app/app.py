from flask import Flask, request, jsonify
from flask_jwt_extended import JWTManager, create_access_token, create_refresh_token
from flask_cors import CORS
from datetime import timedelta
import os

# Import models and uitilities
from models import db
from models.user import User
from models.recipe import Recipe
from models.comment import Comment
from models.ratings import Rating
from models.payment import Payment
from models.ai_request import AIRequest
from models.tag import Tag

from routes.auth_routes import auth_bp
from routes.recipe_routes import recipe_bp
from routes.comment_routes import comment_bp
from routes.rating_routes import rating_bp
from routes.payment_routes import payment_bp
from routes.ai_routes import ai_bp
from routes.user_routes import user_bp
from routes.tag_routes import tag_bp
from routes.admin_routes import admin_bp

def create_app(config_name='development'):
    app = Flask(__name__)
    
    # Configuration
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-secret-key')
    app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'postgresql://user:pass@localhost/recipe_db')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['JWT_SECRET_KEY'] = os.environ.get('JWT_SECRET_KEY', app.config['SECRET_KEY'])
    app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(days=1)
    app.config['JWT_REFRESH_TOKEN_EXPIRES'] = timedelta(days=30)
    
    # Initialize extensions
    db.init_app(app)
    jwt = JWTManager(app)
    CORS(app)
    
    # Register blueprints
    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    app.register_blueprint(recipe_bp, url_prefix='/api/recipes')
    app.register_blueprint(comment_bp, url_prefix='/api/comments')
    app.register_blueprint(rating_bp, url_prefix='/api/ratings')
    app.register_blueprint(payment_bp, url_prefix='/api/payments')
    app.register_blueprint(ai_bp, url_prefix='/api/ai')
    app.register_blueprint(user_bp, url_prefix='/api/users')
    app.register_blueprint(tag_bp, url_prefix='/api/tags')
    app.register_blueprint(admin_bp, url_prefix='/api/admin')
    
    # Error handlers
    @app.errorhandler(404)
    def not_found(error):
        return jsonify({'error': 'Resource not found'}), 404
    
    @app.errorhandler(500)
    def internal_error(error):
        db.session.rollback()
        return jsonify({'error': 'Internal server error'}), 500
    
    # Health check endpoint
    @app.route('/api/health')
    def health_check():
        return jsonify({'status': 'healthy', 'message': 'Recipe API is running'}), 200
    
    return app