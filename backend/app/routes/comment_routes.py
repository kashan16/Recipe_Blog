from datetime import datetime
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from marshmallow import ValidationError

from models import db
from models.comment import Comment
from models.recipe import Recipe
from models.schemas import CommentCreateSchema
from sqlalchemy import desc
from utils.helpers import log_audit_event

comment_bp = Blueprint('comments', __name__)

@comment_bp.route('/recipe/<recipe_id>', methods=['GET'])
def get_recipe_comments(recipe_id):
    """Get comments for a specific recipe"""
    page = request.args.get('page', 1, type=int)
    per_page = min(request.args.get('per_page', 20, type=int), 100)
    
    # Verify recipe exists
    recipe = Recipe.query.filter_by(id=recipe_id, is_deleted=False).first()
    if not recipe:
        return jsonify({'error': 'Recipe not found'}), 404
    
    # Get top-level comments (no parent)
    comments = Comment.query.filter_by(
        recipe_id=recipe_id, 
        parent_id=None,
        is_deleted=False
    ).order_by(desc(Comment.created_at)).paginate(
        page=page, per_page=per_page, error_out=False
    )
    
    return jsonify({
        'comments': [comment.to_dict(include_replies=True) for comment in comments.items],
        'pagination': {
            'page': page,
            'pages': comments.pages,
            'per_page': per_page,
            'total': comments.total,
            'has_next': comments.has_next,
            'has_prev': comments.has_prev
        }
    }), 200

@comment_bp.route('/recipe/<recipe_id>', methods=['POST'])
@jwt_required()
def create_comment(recipe_id):
    """Create a new comment on a recipe"""
    current_user_id = get_jwt_identity()
    
    # Verify recipe exists
    recipe = Recipe.query.filter_by(id=recipe_id, is_deleted=False).first()
    if not recipe:
        return jsonify({'error': 'Recipe not found'}), 404
    
    try:
        schema = CommentCreateSchema()
        data = schema.load(request.get_json())
    except ValidationError as err:
        return jsonify({'error': 'Validation failed', 'details': err.messages}), 400
    
    # Verify parent comment exists if specified
    if data.get('parent_id'):
        parent_comment = Comment.query.filter_by(
            id=data['parent_id'],
            recipe_id=recipe_id,
            is_deleted=False
        ).first()
        if not parent_comment:
            return jsonify({'error': 'Parent comment not found'}), 404
    
    try:
        comment = Comment(
            content=data['content'],
            user_id=current_user_id,
            recipe_id=recipe_id,
            parent_id=data.get('parent_id')
        )
        
        db.session.add(comment)
        db.session.commit()
        
        # Log comment creation
        log_audit_event(
            user_id=current_user_id,
            action='CREATE',
            table_name='comments',
            record_id=comment.id,
            ip_address=request.remote_addr
        )
        
        return jsonify({
            'message': 'Comment created successfully',
            'comment': comment.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Comment creation failed', 'details': str(e)}), 500

@comment_bp.route('/<comment_id>', methods=['PUT'])
@jwt_required()
def update_comment(comment_id):
    """Update a comment"""
    current_user_id = get_jwt_identity()
    
    comment = Comment.query.filter_by(id=comment_id, is_deleted=False).first()
    
    if not comment:
        return jsonify({'error': 'Comment not found'}), 404
    
    if str(comment.user_id) != current_user_id:
        return jsonify({'error': 'Not authorized to update this comment'}), 403
    
    try:
        data = request.get_json()
        content = data.get('content', '').strip()
        
        if not content or len(content) > 1000:
            return jsonify({'error': 'Invalid content length'}), 400
        
        comment.content = content
        comment.is_edited = True
        comment.edited_at = datetime.utcnow()
        
        db.session.commit()
        
        return jsonify({
            'message': 'Comment updated successfully',
            'comment': comment.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Comment update failed', 'details': str(e)}), 500

@comment_bp.route('/<comment_id>', methods=['DELETE'])
@jwt_required()
def delete_comment(comment_id):
    """Delete a comment (soft delete)"""
    current_user_id = get_jwt_identity()
    
    comment = Comment.query.filter_by(id=comment_id, is_deleted=False).first()
    
    if not comment:
        return jsonify({'error': 'Comment not found'}), 404
    
    if str(comment.user_id) != current_user_id:
        return jsonify({'error': 'Not authorized to delete this comment'}), 403
    
    try:
        comment.is_deleted = True
        db.session.commit()
        
        # Log deletion
        log_audit_event(
            user_id=current_user_id,
            action='DELETE',
            table_name='comments',
            record_id=comment.id,
            ip_address=request.remote_addr
        )
        
        return jsonify({'message': 'Comment deleted successfully'}), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Comment deletion failed', 'details': str(e)}), 500
