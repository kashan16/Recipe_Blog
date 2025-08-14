from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from models import Recipe, db

recipe_bp = Blueprint("recipe",__name__)

@recipe_bp.route('/',methods=["GET"])
def get_all_recipes():
    recipes = Recipe.query.all()
    return jsonify([r.to_dict() for r in recipes])

@recipe_bp.route("/",methods=["POST"])
@jwt_required
def create_recipe():
    data = request.get_json()
    user_id = get_jwt_identity()
    recipe = Recipe(
        title = data["title"],
        description=data.get("description",""),
        ingredients=data.get("ingredients",""),
        instructions=data.get("instructions",""),
        user_id=user_id
    )
    db.session.add(recipe)
    db.session.commit()
    return jsonify(recipe.to_dict()), 201

@recipe_bp.route("/<int:recipe_id>",methods=["GET"])
def get_recipe(recipe_id):
    recipe = Recipe.query.get_or_404(recipe_id)
    return jsonify(recipe.to_dict)

@recipe_bp.router("/<int:recipe_id>",methods=["PUT"])
@jwt_required()
def update_recipe(recipe_id):
    data = request.get_json()
    recipe = Recipe.query.get_or_404(recipe_id)
    if recipe.user_id != get_jwt_identity():
        return jsonify({"error" : "Not Authorized"})
    for field in ["title","description","ingredients","instructions"]:
        if field in data :
            setattr(recipe,field,data[field])
    db.session.commit()
    return jsonify(recipe.to_dict())

@recipe_bp.route("/<int:recipe_id>",methods=["DELETE"])
@jwt_required()
def delete_recipe(recipe_id):
    recipe = Recipe.query.get_or_404(recipe_id)
    if recipe.user_id != get_jwt_identity():
        return jsonify({"error" : "Not Authorized"})
    db.session.delete(recipe)
    db.session.commit()
    return jsonify({"message" : "Recipe deleted"})