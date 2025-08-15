from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity

from models import db
from models.tag import Tag
from models.recipe import Recipe
from sqlalchemy import desc

tag_bp = Blueprint('tags', __name__)

@tag_bp.route('', methods=['GET'])
def get_tags():
    """Get all tags with optional search"""
    search = request.args.get('search', '').strip()
    limit = min(request.args.get('limit', 50, type=int), 100)
    
    query = Tag.query
    
    if search:
        query = query.filter(Tag.name.ilike(f'%{search}%'))
    
    tags = query.order_by(desc(Tag.usage_count)).limit(limit).all()
    
    return jsonify({
        'tags': [tag.to_dict() for tag in tags],
        'total': len(tags)
    }), 200

@tag_bp.route('/popular', methods=['GET'])
def get_popular_tags():
    """Get most popular tags"""
    limit = min(request.args.get('limit', 20, type=int), 50)
    
    tags = Tag.query.filter(Tag.usage_count > 0).order_by(
        desc(Tag.usage_count)
    ).limit(limit).all()
    
    return jsonify({
        'tags': [tag.to_dict() for tag in tags],
        'total': len(tags)
    }), 200

@tag_bp.route('/<tag_id>/recipes', methods=['GET'])
def get_tag_recipes(tag_id):
    """Get recipes by tag"""
    page = request.args.get('page', 1, type=int)
    per_page = min(request.args.get('per_page', 10, type=int), 50)
    
    tag = Tag.query.get(tag_id)
    if not tag:
        return jsonify({'error': 'Tag not found'}), 404
    
    recipes = Recipe.query.join(Recipe.tags).filter(
        Tag.id == tag_id,
        Recipe.is_deleted == False
    ).order_by(desc(Recipe.created_at)).paginate(
        page=page, per_page=per_page, error_out=False
    )
    
    return jsonify({
        'tag': tag.to_dict(),
        'recipes': [recipe.to_dict(include_relations=True) for recipe in recipes.items],
        'pagination': {
            'page': page,
            'pages': recipes.pages,
            'per_page': per_page,
            'total': recipes.total,
            'has_next': recipes.has_next,
            'has_prev': recipes.has_prev
        }
    }), 200
