import uuid
from sqlalchemy.dialects.postgresql import UUID
from . import db

class RecipeTag(db.Model):
    __tablename__ = "recipe_tags"
    
    recipe_id = db.Column(UUID(as_uuid=True), db.ForeignKey("recipes.id"), primary_key=True)
    tag_id = db.Column(UUID(as_uuid=True), db.ForeignKey("tags.id"), primary_key=True)
    created_at = db.Column(db.DateTime, default=db.func.now())