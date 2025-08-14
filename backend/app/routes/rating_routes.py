from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from models import Rating, Recipe, db

rating_bp = Blueprint("ratings", __name__)

@rating_bp.route("/<int:recipe_id>", methods=["POST"])
@jwt_required()
def add_rating(recipe_id):
    data = request.get_json()
    rating_value = data.get("rating")
    if not (1 <= rating_value <= 5):
        return jsonify({"error": "Rating must be 1-5"}), 400

    existing = Rating.query.filter_by(recipe_id=recipe_id, user_id=get_jwt_identity()).first()
    if existing:
        existing.rating = rating_value
    else:
        db.session.add(Rating(recipe_id=recipe_id, user_id=get_jwt_identity(), rating=rating_value))
    db.session.commit()
    return jsonify({"message": "Rating saved"})

@rating_bp.route("/<int:recipe_id>", methods=["GET"])
def get_recipe_ratings(recipe_id):
    ratings = Rating.query.filter_by(recipe_id=recipe_id).all()
    avg_rating = sum(r.rating for r in ratings) / len(ratings) if ratings else 0
    return jsonify({"average": avg_rating, "count": len(ratings)})
