from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity, create_access_token, create_refresh_token
from marshmallow import ValidationError
from datetime import datetime

from models import db
from models.user import User
from models.schemas import UserRegistrationSchema, UserLoginSchema
from app.utils.helpers import log_audit_event

auth_bp = Blueprint('auth',__name__)

@auth_bp.route('/register',methods=['POST'])
def register():
    """Register new user"""
    try :
        schema = UserRegistrationSchema()
        data = schema.load(request.get_json())
    except ValidationError as err:
        return jsonify({'error' : 'Validation failed', 'details' : err.messages }), 400
    
    # Check if user already exists
    if User.query.filter_by(email=data['email']).first():
        return jsonify({'error' : 'Email already registered' }), 409
    
    if User.query.filter_by(username=data['username']).first():
        return jsonify({'error' : 'Username already taken' }), 409
    
    try :
        user = User(
            username = data['username'],
            email = data['email'],
            first_name = data.get('first_name'),
            last_name = data.get('last_name')
        )
        user.set_password(data['password'])
        
        db.session.add(user)
        db.session.commit
        
        # Log registration
        log_audit_event(
            user_id = user.id,
            action = 'CREATE',
            table_name = 'users',
            record_id = user.id,
            id_address = request.remote_addr,
            user_agent = request.headers.get('User-Agent')
        )
        
        # Create tokens
        access_token = create_access_token(identity=str(user.id))
        refresh_token = create_refresh_token(identity=str(user.id))
        
        return jsonify({
            'message' : 'User registered successfully',
            'user' : user.to_dict(),
            'access_token' : access_token,
            'refresh_token' : refresh_token
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error' : 'Registration failed', 'details' : str(e)}), 500
    
@auth_bp.route('/login',methods=['POST'])
def login():
    """Login user"""
    try :
        schema = UserLoginSchema()
        data = schema.load(request.get_json())
    except ValidationError as err:
        return jsonify({'error' : 'Validation failed', 'details' : err.messages }), 400
    
    # We find the user first(by hitting up email in our users table)
    user = User.query.filter_by(email=data['email']).first()
    
    if not user or not user.check_password(data['password']):
      return jsonify({ 'error' : 'Invaild email or password' }), 401
  
    if not user.is_active:
        return jsonify({ 'error' : "Account is deactivated" }), 401
    
    # Upadte last login
    user.last_login = datetime.utcnow()
    db.session.commit()

    # Log login
    log_audit_event(
        user_id=user.id,
        action='LOGIN',
        table_name='users',
        record_id=user.id,
        ip_address=request.remote_addr,
        user_agent=request.headers.get('User-Agent')
    )
    
    access_token = create_access_token(identity=str(user.id))
    refresh_token = create_refresh_token(identity=str(user.id))
    
    return jsonify({
        'message' : 'Login successful',
        'user' : user.to_dict(),
        'access_token' : access_token,
        'refresh_token' : refresh_token
    }), 200
    
@auth_bp.route('/refresh', methods=['POST'])
@jwt_required(refresh=True)
def refresh():
    """Refresh access token"""
    current_user_id = get_jwt_identity()
    user = User.query.get(current_user_id)
    
    if not user or not user.is_active:
        return jsonify({'error': 'User not found or inactive'}), 404
    
    access_token = create_access_token(identity=current_user_id)
    return jsonify({'access_token': access_token}), 200

@auth_bp.route('/me', methods=['GET'])
@jwt_required()
def get_current_user():
    """Get current user profile"""
    current_user_id = get_jwt_identity()
    user = User.query.get(current_user_id)
    
    if not user:
        return jsonify({'error': 'User not found'}), 404
    
    return jsonify({'user': user.to_dict(include_sensitive=True)}), 200    