from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from marshmallow import ValidationError
from sqlalchemy import desc
from sqlalchemy.exc import IntegrityError

from models import db
from models.ratings import Rating
from models.recipe import Recipe
from models.schemas import RatingCreateSchema
from utils.helpers import log_audit_event

rating_bp = Blueprint('ratings', __name__)

@rating_bp.route('/recipe/<recipe_id>', methods=['POST'])
@jwt_required()
def create_or_update_rating(recipe_id):
    """Create or update a rating for a recipe"""
    current_user_id = get_jwt_identity()
    
    # Verify recipe exists
    recipe = Recipe.query.filter_by(id=recipe_id, is_deleted=False).first()
    if not recipe:
        return jsonify({'error': 'Recipe not found'}), 404
    
    # Check if user is rating their own recipe
    if str(recipe.author_id) == current_user_id:
        return jsonify({'error': 'Cannot rate your own recipe'}), 403
    
    try:
        schema = RatingCreateSchema()
        data = schema.load(request.get_json())
    except ValidationError as err:
        return jsonify({'error': 'Validation failed', 'details': err.messages}), 400
    
    try:
        # Check if rating already exists
        existing_rating = Rating.query.filter_by(
            user_id=current_user_id,
            recipe_id=recipe_id
        ).first()
        
        if existing_rating:
            # Update existing rating
            old_score = existing_rating.score
            existing_rating.score = data['score']
            existing_rating.review = data.get('review')
            
            db.session.commit()
            
            # Log update
            log_audit_event(
                user_id=current_user_id,
                action='UPDATE',
                table_name='ratings',
                record_id=existing_rating.id,
                changes={'old_score': old_score, 'new_score': data['score']},
                ip_address=request.remote_addr
            )
            
            return jsonify({
                'message': 'Rating updated successfully',
                'rating': existing_rating.to_dict()
            }), 200
        else:
            # Create new rating
            rating = Rating(
                score=data['score'],
                review=data.get('review'),
                user_id=current_user_id,
                recipe_id=recipe_id
            )
            
            db.session.add(rating)
            db.session.commit()
            
            # Log creation
            log_audit_event(
                user_id=current_user_id,
                action='CREATE',
                table_name='ratings',
                record_id=rating.id,
                ip_address=request.remote_addr
            )
            
            return jsonify({
                'message': 'Rating created successfully',
                'rating': rating.to_dict()
            }), 201
            
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Rating operation failed', 'details': str(e)}), 500

@rating_bp.route('/recipe/<recipe_id>', methods=['GET'])
def get_recipe_ratings(recipe_id):
    """Get all ratings for a specific recipe"""
    page = request.args.get('page', 1, type=int)
    per_page = min(request.args.get('per_page', 10, type=int), 50)
    
    # Verify recipe exists
    recipe = Recipe.query.filter_by(id=recipe_id, is_deleted=False).first()
    if not recipe:
        return jsonify({'error': 'Recipe not found'}), 404
    
    ratings = Rating.query.filter_by(recipe_id=recipe_id).order_by(
        desc(Rating.created_at)
    ).paginate(page=page, per_page=per_page, error_out=False)
    
    # Calculate statistics
    all_ratings = Rating.query.filter_by(recipe_id=recipe_id).all()
    avg_rating = sum(r.score for r in all_ratings) / len(all_ratings) if all_ratings else 0
    rating_distribution = {i: 0 for i in range(1, 6)}
    for rating in all_ratings:
        rating_distribution[rating.score] += 1
    
    return jsonify({
        'ratings': [rating.to_dict() for rating in ratings.items],
        'statistics': {
            'average_rating': round(avg_rating, 2),
            'total_ratings': len(all_ratings),
            'distribution': rating_distribution
        },
        'pagination': {
            'page': page,
            'pages': ratings.pages,
            'per_page': per_page,
            'total': ratings.total,
            'has_next': ratings.has_next,
            'has_prev': ratings.has_prev
        }
    }), 200

@rating_bp.route('/<rating_id>', methods=['DELETE'])
@jwt_required()
def delete_rating(rating_id):
    """Delete a rating"""
    current_user_id = get_jwt_identity()
    
    rating = Rating.query.get(rating_id)
    
    if not rating:
        return jsonify({'error': 'Rating not found'}), 404
    
    if str(rating.user_id) != current_user_id:
        return jsonify({'error': 'Not authorized to delete this rating'}), 403
    
    try:
        db.session.delete(rating)
        db.session.commit()
        
        # Log deletion
        log_audit_event(
            user_id=current_user_id,
            action='DELETE',
            table_name='ratings',
            record_id=rating_id,
            ip_address=request.remote_addr
        )
        
        return jsonify({'message': 'Rating deleted successfully'}), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Rating deletion failed', 'details': str(e)}), 500
