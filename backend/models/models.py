import uuid
from datetime import datetime
from sqlalchemy.dialects.postgresql import UUID, JSONB, ARRAY
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

def gen_uuid():
    return str(uuid.uuid4())

class User(db.Model):
    __tablename__ = "users"
    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = db.Column(db.String(255), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.Text, nullable=False)
    name = db.Column(db.String(255))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    free_generation_used = db.Column(db.Integer, default=0)  # Fixed: was "deafult"
    credit_balance = db.Column(db.Integer, default=0)
    subscription_status = db.Column(db.String(50), default="free")
    stripe_customer_id = db.Column(db.String(255), nullable=True)
    pantry_items = db.relationship("PantryItem", back_populates="user", cascade="all, delete-orphan")  # Fixed: removed space in cascade
    favorites = db.relationship("Favorite", back_populates="user")
    
class PantryItem(db.Model):
    __tablename__ = "pantry_items"
    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = db.Column(UUID(as_uuid=True), db.ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)  # Fixed: was "ForeingKey"
    raw_name = db.Column(db.Text, nullable=False)
    normalized_name = db.Column(db.Text, nullable=False, index=True)
    quantity = db.Column(db.Text)
    unit = db.Column(db.String(50))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    user = db.relationship("User", back_populates="pantry_items")  # Fixed: was "pantry_item"
    
class Recipe(db.Model):
    __tablename__ = "recipes"
    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    title = db.Column(db.Text, nullable=False, index=True)  # Fixed: was "db.text"
    author_id = db.Column(UUID(as_uuid=True), db.ForeignKey("users.id"), nullable=True)
    source = db.Column(db.String(50), nullable=False, default="user")
    cuisine = db.Column(db.String(100))
    diet_tags = db.Column(ARRAY(db.String(100)))
    servings = db.Column(db.Integer)
    cooking_time_minutes = db.Column(db.Integer)
    raw = db.Column(JSONB)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, onupdate=datetime.utcnow)
    
class RecipeIngredient(db.Model):
    __tablename__ = "recipe_ingredients"
    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    recipe_id = db.Column(UUID(as_uuid=True), db.ForeignKey("recipes.id", ondelete="CASCADE"), nullable=False, index=True)
    ingredient_id = db.Column(UUID(as_uuid=True), nullable=True)
    name = db.Column(db.Text, nullable=False)
    quantity = db.Column(db.Text)
    position = db.Column(db.Integer, default=0)
    
class Favorite(db.Model):
    __tablename__ = "favorites"
    user_id = db.Column(UUID(as_uuid=True), db.ForeignKey("users.id", ondelete="CASCADE"), primary_key=True)
    recipe_id = db.Column(UUID(as_uuid=True), db.ForeignKey("recipes.id", ondelete="CASCADE"), primary_key=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    user = db.relationship("User", back_populates="favorites")

class AIGeneration(db.Model):
    __tablename__ = "ai_generations"
    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = db.Column(UUID(as_uuid=True), db.ForeignKey("users.id"))
    prompt_hash = db.Column(db.String(128), index=True)
    input_payload = db.Column(JSONB)
    prompt_text = db.Column(db.Text)
    response_json = db.Column(JSONB)
    model = db.Column(db.String(100))
    tokens_prompt = db.Column(db.Integer)
    tokens_completion = db.Column(db.Integer)
    cost_cents = db.Column(db.Integer)
    cached = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow) 