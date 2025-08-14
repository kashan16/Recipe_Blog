from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from werkzeug.security import generate_password_hash, check_password_hash
from models import User, db
from datetime import timedelta

auth_bp = Blueprint("auth",__name__)

@auth_bp.route("/signup",methods=["POST"])
def signup():
    data = request.get_json()
    
    if not data.get("email") or not data.get("password") :
        return jsonify({"error" : "Email and password required"}), 400
    
    if User.query.filter_by(email=data["email"]).first():
        return jsonify({"email" : "Email already registered"}), 400
    
    hashed_pw = generate_password_hash(data["password"])
    user = User(email=data["email"],password_hash=hashed_pw)
    db.session.add(user)
    db.session.commit()
    return jsonify({"message" : "User created successfully"}), 201

@auth_bp.route("/login",methods=["POST"])
def login():
    data = request.get_json()
    user = User.query.filter_by(email=data.get("email")).first()
    if not user or not check_password_hash(user.password_hash,data.get("password")):
        return jsonify({"error" : "Invalid login credentials"}), 401
    
    access_token = create_access_token(identity=user.id,expires_delta=timedelta(days=1))
    return jsonify({"access_token" : access_token, "user_id" : user.id})

@auth_bp.route("/me",methods=["GET"])
@jwt_required
def get_profile():
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    return jsonify({"id" : user.id , "email" : user.email})

