from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from marshmallow import ValidationError
from datetime import datetime

from models import db
from models.user import User
from models.recipe import Recipe
from sqlalchemy import desc
from utils.helpers import save_picture, allowed_file, log_audit_event

user_bp = Blueprint('users', __name__)

@user_bp.route('/profile', methods=['GET'])
@jwt_required()
def get_profile():
    """Get current user profile"""
    current_user_id = get_jwt_identity()
    user = User.query.get(current_user_id)
    
    if not user:
        return jsonify({'error': 'User not found'}), 404
    
    # Get user statistics
    recipe_count = Recipe.query.filter_by(author_id=current_user_id, is_deleted=False).count()
    
    profile_data = user.to_dict(include_sensitive=True)
    profile_data['statistics'] = {
        'recipes_count': recipe_count,
        'member_since': user.created_at.strftime('%B %Y')
    }
    
    return jsonify({'profile': profile_data}), 200

@user_bp.route('/profile', methods=['PUT'])
@jwt_required()
def update_profile():
    """Update current user profile"""
    current_user_id = get_jwt_identity()
    user = User.query.get(current_user_id)
    
    if not user:
        return jsonify({'error': 'User not found'}), 404
    
    data = request.get_json()
    
    # Store old data for audit
    old_data = user.to_dict(include_sensitive=True)
    
    # Update allowed fields
    allowed_fields = ['first_name', 'last_name', 'bio', 'username']
    for field in allowed_fields:
        if field in data:
            # Check username uniqueness
            if field == 'username' and data[field] != user.username:
                existing_user = User.query.filter_by(username=data[field]).first()
                if existing_user:
                    return jsonify({'error': 'Username already taken'}), 409
            setattr(user, field, data[field])
    
    try:
        db.session.commit()
        
        # Log profile update
        log_audit_event(
            user_id=current_user_id,
            action='UPDATE',
            table_name='users',
            record_id=user.id,
            changes={'old': old_data, 'new': user.to_dict(include_sensitive=True)},
            ip_address=request.remote_addr
        )
        
        return jsonify({
            'message': 'Profile updated successfully',
            'profile': user.to_dict(include_sensitive=True)
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Profile update failed', 'details': str(e)}), 500

@user_bp.route('/profile/image', methods=['POST'])
@jwt_required()
def upload_profile_image():
    """Upload profile image"""
    current_user_id = get_jwt_identity()
    user = User.query.get(current_user_id)
    
    if not user:
        return jsonify({'error': 'User not found'}), 404
    
    if 'image' not in request.files:
        return jsonify({'error': 'No image file provided'}), 400
    
    file = request.files['image']
    
    if file.filename == '' or not allowed_file(file.filename):
        return jsonify({'error': 'Invalid file type'}), 400
    
    try:
        # Save the image
        filename = save_picture(file, 'profile_pics')
        
        # Update user profile
        user.profile_image_url = f'/static/profile_pics/{filename}'
        db.session.commit()
        
        return jsonify({
            'message': 'Profile image updated successfully',
            'image_url': user.profile_image_url
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Image upload failed', 'details': str(e)}), 500

@user_bp.route('/<user_id>', methods=['GET'])
def get_user_public_profile(user_id):
    """Get public user profile"""
    user = User.query.filter_by(id=user_id, is_active=True, is_deleted=False).first()
    
    if not user:
        return jsonify({'error': 'User not found'}), 404
    
    # Get user statistics
    recipe_count = Recipe.query.filter_by(author_id=user_id, is_deleted=False).count()
    
    profile_data = user.to_dict(include_sensitive=False)
    profile_data['statistics'] = {
        'recipes_count': recipe_count,
        'member_since': user.created_at.strftime('%B %Y')
    }
    
    return jsonify({'profile': profile_data}), 200

@user_bp.route('/<user_id>/recipes', methods=['GET'])
def get_user_recipes(user_id):
    """Get public recipes by a specific user"""
    page = request.args.get('page', 1, type=int)
    per_page = min(request.args.get('per_page', 10, type=int), 50)
    
    user = User.query.filter_by(id=user_id, is_active=True, is_deleted=False).first()
    if not user:
        return jsonify({'error': 'User not found'}), 404
    
    recipes = Recipe.query.filter_by(
        author_id=user_id, 
        is_deleted=False
    ).order_by(desc(Recipe.created_at)).paginate(
        page=page, per_page=per_page, error_out=False
    )
    
    return jsonify({
        'recipes': [recipe.to_dict(include_relations=True) for recipe in recipes.items],
        'user': user.to_dict(include_sensitive=False),
        'pagination': {
            'page': page,
            'pages': recipes.pages,
            'per_page': per_page,
            'total': recipes.total,
            'has_next': recipes.has_next,
            'has_prev': recipes.has_prev
        }
    }), 200
