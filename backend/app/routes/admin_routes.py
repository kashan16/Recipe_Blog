from datetime import datetime
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from sqlalchemy import desc, func

from models import db
from models.user import User
from models.recipe import Recipe
from models.payment import Payment
from models.ai_request import AIRequest
from app.utils.helpers import log_audit_event
from utils.decorators import admin_required

admin_bp = Blueprint('admin', __name__)

@admin_bp.route('/dashboard', methods=['GET'])
@admin_required
def admin_dashboard():
    """Get admin dashboard statistics"""
    
    # User statistics
    total_users = User.query.filter_by(is_deleted=False).count()
    premium_users = User.query.filter_by(is_premium=True, is_deleted=False).count()
    new_users_today = User.query.filter(
        User.created_at >= datetime.utcnow().date()
    ).count()
    
    # Recipe statistics
    total_recipes = Recipe.query.filter_by(is_deleted=False).count()
    featured_recipes = Recipe.query.filter_by(is_featured=True, is_deleted=False).count()
    
    # Payment statistics
    total_payments = Payment.query.count()
    completed_payments = Payment.query.filter_by(status='completed').count()
    total_revenue = db.session.query(func.sum(Payment.amount)).filter_by(
        status='completed'
    ).scalar() or 0
    
    # AI usage statistics
    total_ai_requests = AIRequest.query.count()
    successful_ai_requests = AIRequest.query.filter_by(status='completed').count()
    
    return jsonify({
        'users': {
            'total': total_users,
            'premium': premium_users,
            'new_today': new_users_today
        },
        'recipes': {
            'total': total_recipes,
            'featured': featured_recipes
        },
        'payments': {
            'total': total_payments,
            'completed': completed_payments,
            'revenue': float(total_revenue)
        },
        'ai_usage': {
            'total_requests': total_ai_requests,
            'successful': successful_ai_requests
        }
    }), 200

@admin_bp.route('/users', methods=['GET'])
@admin_required
def admin_get_users():
    """Get all users for admin"""
    page = request.args.get('page', 1, type=int)
    per_page = min(request.args.get('per_page', 20, type=int), 100)
    search = request.args.get('search', '').strip()
    
    query = User.query.filter_by(is_deleted=False)
    
    if search:
        query = query.filter(
            User.username.ilike(f'%{search}%') |
            User.email.ilike(f'%{search}%')
        )
    
    users = query.order_by(desc(User.created_at)).paginate(
        page=page, per_page=per_page, error_out=False
    )
    
    return jsonify({
        'users': [user.to_dict(include_sensitive=True) for user in users.items],
        'pagination': {
            'page': page,
            'pages': users.pages,
            'per_page': per_page,
            'total': users.total,
            'has_next': users.has_next,
            'has_prev': users.has_prev
        }
    }), 200

@admin_bp.route('/recipes/<recipe_id>/feature', methods=['POST'])
@admin_required
def admin_feature_recipe(recipe_id):
    """Feature/unfeature a recipe"""
    current_user_id = get_jwt_identity()
    
    recipe = Recipe.query.filter_by(id=recipe_id, is_deleted=False).first()
    if not recipe:
        return jsonify({'error': 'Recipe not found'}), 404
    
    recipe.is_featured = not recipe.is_featured
    db.session.commit()
    
    # Log admin action
    log_audit_event(
        user_id=current_user_id,
        action='ADMIN_FEATURE' if recipe.is_featured else 'ADMIN_UNFEATURE',
        table_name='recipes',
        record_id=recipe.id,
        ip_address=request.remote_addr
    )
    
    return jsonify({
        'message': f'Recipe {"featured" if recipe.is_featured else "unfeatured"} successfully',
        'recipe': recipe.to_dict()
    }), 200

#@admin_bp.route('/audit-logs', methods=['GET'])
#@admin_required
# def get_audit_logs():
#    """Get audit logs for admin"""
#    page = request.args.get('page', 1, type=int)
#    per_page = min(request.args.get('per_page', 50, type=int), 100)
#    action = request.args.get('action')
#    table_name = request.args.get('table_name')
#    
#    query = AuditLog.query
#    
#    if action:
#        query = query.filter_by(action=action)
#    if table_name:
#        query = query.filter_by(table_name=table_name)
#    
#    logs = query.order_by(desc(AuditLog.created_at)).paginate(
#        page=page, per_page=per_page, error_out=False
#    )
#    
#    return jsonify({
#        'logs': [log.to_dict() for log in logs.items],
#        'pagination': {
#            'page': page,
#            'pages': logs.pages,
#            'per_page': per_page,
#            'total': logs.total,
#            'has_next': logs.has_next,
#            'has_prev': logs.has_prev
#        }
#    }), 200