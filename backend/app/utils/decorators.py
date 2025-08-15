from functools import wraps
from flask import request, jsonify, g
from flask_jwt_extended import jwt_required, get_jwt_identity
from models.user import User

def premium_required(f):
    """Decorator to check if user has premium subscription"""
    @wraps(f)
    @jwt_required()
    def decorated_function(*args, **kwargs):
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)
        
        if not user or not user.is_premium :
            return jsonify({'error' : "Premium subscription required"}), 403
        
        g.current_user = user
        return f(*args,**kwargs)
    
    return decorated_function

def admin_required(f):
    """Decorator to check if user is admin"""
    @wraps(f)
    @jwt_required()
    def decorated_function(*args,**kwargs):
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)
        
        if not user or not getattr(user, 'is_admin', False) : 
            return jsonify({"error" : "Admin access required"}), 403
    
        g.current_user = user
        return f(*args,**kwargs)
    
    return decorated_function

def rate_limit_by_user(max_requests=100, per_seconds=3600):
    """Rate limiting decorator based on user"""
    def decorator(f):
        @wraps(f)
        @jwt_required()
        def decorated_function(*args, **kwargs):
            # Implementation would depend caching solution (Redis)
            # This is a placeholder for the concept
            current_user_id = get_jwt_identity()
            # Check rate limit logic here
            return f(*args, **kwargs)
        return decorated_function
    return decorator