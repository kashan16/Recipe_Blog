from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from marshmallow import ValidationError
from sqlalchemy import desc, asc

from models import db
from models.recipe import Recipe
from models.user import User
from models.tag import Tag
from models.schemas import RecipeCreateSchema, RecipeUpdateSchema
from app.utils.helpers import log_audit_event

recipe_bp = Blueprint('recipe',__name__)

@recipe_bp.route('',methods=['GET'])
def get_recipe():
    """Get all recipes with pagination and filtering"""
    page = request.args.get('page',1,type=int)
    per_page = min(request.args.get('per_page',10,type=int),100)
    
    # Filtering options
    difficulty = request.args.get('difficulty')
    featured = request.args.get('featured', type=bool)
    author_id = request.args.get('author_id')
    tag = request.args.get('tag')
    search = request.args.get('search')
    sort_by = request.args.get('sort_by', 'created_at')
    sort_order = request.args.get('sort_order', 'desc')
    
    # Build query
    query = Recipe.query.filter_by(is_deleted=False)
    
    if difficulty:
        query = query.filter_by(difficulty_level=difficulty)
    if featured is not None:
        query = query.filter_by(is_featured=featured)
    if author_id:
        query = query.filter_by(author_id=author_id)
    if tag:
        query = query.join(Recipe.tags).filter(Tag.name.ilike(f'%{tag}%'))
    if search:
        query = query.filter(
            Recipe.title.ilike(f'%{search}%') |
            Recipe.description.ilike(f'%{search}%') |
            Recipe.ingredients.ilike(f'%{search}%')
        )        
    # Apply sorting
    if sort_order == 'desc':
        query = query.order_by(desc(getattr(Recipe, sort_by, Recipe.created_at)))
    else:
        query = query.order_by(asc(getattr(Recipe, sort_by, Recipe.created_at)))
    
    # Paginate
    recipes = query.paginate(
        page=page, per_page=per_page, error_out=False
    )
    
    return jsonify({
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
@recipe_bp.route('/<recipe_id>', methods=['GET'])
def get_recipe(recipe_id):
    """Get single recipe by ID"""
    recipe = Recipe.query.filter_by(id=recipe_id, is_deleted=False).first()
    
    if not recipe:
        return jsonify({'error': 'Recipe not found'}), 404
    
    # Increment view count
    recipe.view_count += 1
    db.session.commit()
    
    return jsonify({'recipe': recipe.to_dict(include_relations=True)}), 200

@recipe_bp.route('', methods=['POST'])
@jwt_required()
def create_recipe():
    """Create a new recipe"""
    current_user_id = get_jwt_identity()
    
    try:
        schema = RecipeCreateSchema()
        data = schema.load(request.get_json())
    except ValidationError as err:
        return jsonify({'error': 'Validation failed', 'details': err.messages}), 400
    
    try:
        recipe = Recipe(
            title=data['title'],
            description=data['description'],
            ingredients=data['ingredients'],
            instructions=data['instructions'],
            prep_time=data.get('prep_time'),
            cook_time=data.get('cook_time'),
            servings=data.get('servings'),
            difficulty_level=data.get('difficulty_level', 'medium'),
            author_id=current_user_id
        )
        
        db.session.add(recipe)
        db.session.flush()  # To get the recipe ID
        
        # Add tags
        tag_names = data.get('tags', [])
        for tag_name in tag_names:
            tag = Tag.query.filter_by(name=tag_name.lower()).first()
            if not tag:
                tag = Tag(name=tag_name.lower())
                db.session.add(tag)
            recipe.tags.append(tag)
        
        db.session.commit()
        
        # Log creation
        log_audit_event(
            user_id=current_user_id,
            action='CREATE',
            table_name='recipes',
            record_id=recipe.id,
            ip_address=request.remote_addr
        )
        
        return jsonify({
            'message': 'Recipe created successfully',
            'recipe': recipe.to_dict(include_relations=True)
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Recipe creation failed', 'details': str(e)}), 500

@recipe_bp.route('/<recipe_id>', methods=['PUT'])
@jwt_required()
def update_recipe(recipe_id):
    """Update an existing recipe"""
    current_user_id = get_jwt_identity()
    
    recipe = Recipe.query.filter_by(id=recipe_id, is_deleted=False).first()
    
    if not recipe:
        return jsonify({'error': 'Recipe not found'}), 404
    
    if str(recipe.author_id) != current_user_id:
        return jsonify({'error': 'Not authorized to update this recipe'}), 403
    
    try:
        schema = RecipeUpdateSchema()
        data = schema.load(request.get_json())
    except ValidationError as err:
        return jsonify({'error': 'Validation failed', 'details': err.messages}), 400
    
    try:
        # Store old values for audit
        old_data = recipe.to_dict()
        
        # Update fields
        for field, value in data.items():
            if field != 'tags':
                setattr(recipe, field, value)
        
        # Update tags if provided
        if 'tags' in data:
            recipe.tags.clear()
            for tag_name in data['tags']:
                tag = Tag.query.filter_by(name=tag_name.lower()).first()
                if not tag:
                    tag = Tag(name=tag_name.lower())
                    db.session.add(tag)
                recipe.tags.append(tag)
        
        db.session.commit()
        
        # Log update
        log_audit_event(
            user_id=current_user_id,
            action='UPDATE',
            table_name='recipes',
            record_id=recipe.id,
            changes={'old': old_data, 'new': recipe.to_dict()},
            ip_address=request.remote_addr
        )
        
        return jsonify({
            'message': 'Recipe updated successfully',
            'recipe': recipe.to_dict(include_relations=True)
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Recipe update failed', 'details': str(e)}), 500

@recipe_bp.route('/<recipe_id>', methods=['DELETE'])
@jwt_required()
def delete_recipe(recipe_id):
    """Delete a recipe (soft delete)"""
    current_user_id = get_jwt_identity()
    
    recipe = Recipe.query.filter_by(id=recipe_id, is_deleted=False).first()
    
    if not recipe:
        return jsonify({'error': 'Recipe not found'}), 404
    
    if str(recipe.author_id) != current_user_id:
        return jsonify({'error': 'Not authorized to delete this recipe'}), 403
    
    try:
        recipe.is_deleted = True
        db.session.commit()
        
        # Log deletion
        log_audit_event(
            user_id=current_user_id,
            action='DELETE',
            table_name='recipes',
            record_id=recipe.id,
            ip_address=request.remote_addr
        )
        
        return jsonify({'message': 'Recipe deleted successfully'}), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Recipe deletion failed', 'details': str(e)}), 500

@recipe_bp.route('/my-recipes', methods=['GET'])
@jwt_required()
def get_my_recipes():
    """Get current user's recipes"""
    current_user_id = get_jwt_identity()
    page = request.args.get('page', 1, type=int)
    per_page = min(request.args.get('per_page', 10, type=int), 100)
    
    recipes = Recipe.query.filter_by(
        author_id=current_user_id, 
        is_deleted=False
    ).order_by(desc(Recipe.created_at)).paginate(
        page=page, per_page=per_page, error_out=False
    )
    
    return jsonify({
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
            