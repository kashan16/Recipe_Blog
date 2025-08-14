from datetime import datetime
import uuid
from sqlalchemy.dialects.postgresql import UUID
from . import db

class Tag(db.Model):
    __tablename__ = "tags"
    
    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = db.Column(db.String(50), unique=True, nullable=False, index=True)
    description = db.Column(db.String(200))
    color = db.Column(db.String(7), default="#3B82F6")
    usage_count = db.Column(db.Integer, default=0)
    
    recipes = db.relationship("Recipe", secondary="recipe_tags", back_populates="tags")
        
    def to_dict(self):
        """Convert tag to dictionary"""
        return {
            'id': str(self.id),
            'name': self.name,
            'description': self.description,
            'color': self.color,
            'usage_count': self.usage_count,
            'created_at': self.created_at.isoformat()
        }
    
    def __repr__(self):
        return f"<Tag {self.name}>"