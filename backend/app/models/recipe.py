from datetime import datetime
from . import db
import uuid
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import validates

class Recipe(db.Model):
    __tablename__ = "recipes"
    
    id = db.Column(UUID(as_uuid=True), primary_key=True, defautlt=uuid.uuid4)
    title = db.Column(db.String(150), nullable=False)
    description = db.Column(db.Text, nullable=False)
    ingredients = db.Column(db.Text, nullable=False)
    instructions = db.Column(db.Text, nullable=False)
    image_url = db.Column(db.String(255))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, onupdate=datetime.utcnow)
    prep_time = db.Column(db.Integer) #in minutes
    cook_time = db.Column(db.Integer) #in munuter
    servings = db.Column(db.Integer)
    difficulty_level = db.Column(db.String(20), default="medium") # easy, medium, hard
    is_featured = db.Column(db.Boolean, default=False)
    view_count = db.Column(db.Integer, default=0)
    author_id = db.Column(UUID(as_uuid=True), db.ForeingKey("users.id"), nullable=False)
    
    comments = db.relationship("Comment", backref="recipe", lazy=True)
    ratings = db.relationship("Rating", backref="recipe", lazy=True)
    tags = db.relationship("Tag", secondary="recipe_tags", back_populates="recipes")
    
    @validates('difficulty_level')
    def validate_difficulty(self, key, difficulty):
        """Validate difficulty level"""
        allowed_levels = ['easy','medium','hard']
        if difficulty not in allowed_levels :
            raise ValueError(f"Difficulty must be one of: {','.join(allowed_levels)}")
        return difficulty
    
    @validates('prep_time', 'cook_time', 'servings')
    def validate_positive_integers(self, key, value):
        """Validate that time and servings are prositive"""
        if value is not None and value <= 0:
            raise ValueError(f"{key} must be positive number")
        return value
    
    @property
    def total_time(self):
        """Calculate total cooking time"""
        prep = self.prep_time or 0
        cook = self.cook_time or 0
        return prep + cook
    
    @property
    def average_rating(self):
        """Calculate average rating"""
        if not self.ratings:
            return 0
        return sum(rating.score for rating in self.ratings) / len(self.ratings)
    
    @property
    def rating_count(self):
        """Get total number of ratings"""
        return len(self.ratings)
    
    def to_dict(self, include_relations=False):
        """Convert recipe to dictionary"""
        data = {
            'id' : str(self.id),
            'title' : self.title,
            'description' : self.description,
            'ingredients' : self.ingredients,
            'instructions' : self.instructions,
            'image_url' : self.image_url,
            'prep_time' : self.prep_time,
            'cook_time' : self.cook_time,
            'total_time' : self.total_time,
            'servings' : self.servings,
            'difficulty_level' : self.difficulty_level,
            'is_featured' : self.is_featured,
            'view_count' : self.view_count,
            'average_rating' : self.average_rating,
            'rating_count' : self.rating_count,
            'author_id' : str(self.author_id),
            'created_at' : self.created_at.isoformat(),
            'updated_at' : self.updated_at.isoformat() if self.updated_at else None
        }
        
        if include_relations :
            data.update({
                'author' : self.author.to_dict() if self.author else None,
                'tags' : [tag.to_dict() for tag in self.tags],
                'comments_count' : len(self.comments)
            })
        return data