from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from models import Comment, Recipe, db

comment_bp = Blueprint("comments",__name__)

@comment_bp.route("/<int:recipe_id>",methods=["POST"])
@jwt_required()
def add_comment(recipe_id):
    recipe = Recipe.query.get_or_404(recipe_id)
    data = request.get_json()
    comment = Comment(content=data["content"],user_id=get_jwt_identity(),recipe_id=recipe.id)
    db.session.add(comment)
    db.session.commit()
    return jsonify(comment.to_dict()), 201

@comment_bp.route("/<int:recipe_id>",methods=["GET"])
def get_comments(recipe_id):
    comments = Comment.query.filter_by(recipe_id=recipe_id).all()
    return jsonify([c.to_dict() for c in comments])

@comment_bp.route("/<int:recipe_id>",methods=["DELETE"])
@jwt_required()
def delete_comment(comment_id):
    comment = Comment.query.get_or_404(comment_id)
    if comment.user_id != get_jwt_identity():
        return jsonify({"error" : "Not Authorized"})
    db.session.delete(comment)
    db.session.commit()
    return jsonify({"message" : "Comment deleted"})