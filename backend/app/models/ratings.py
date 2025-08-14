from datetime import datetime
import uuid
from sqlalchemy.dialects.postgresql import UUID
from . import db
from sqlalchemy.orm import validates

class Rating(db.Model):
    __tablename__ = "ratings"
    
    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    score = db.Column(db.Integer, nullable=False)
    review = db.Column(db.Text) # Optional written review
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    user_id = db.Column(UUID(as_uuid=True), db.ForeignKey("users.id"), nullable=False)
    recipe_id = db.Column(UUID(as_uuid=True), db.ForeignKey("recipes.id"), nullable=False)
    
    __table_args__ = (
        db.UniqueConstraint('user_id','recipe_id',name='unique_user_recipe_rating'),
    )
    
    @validates('score')
    def validate_score(self, key, score):
        """Validate rating score is between 1 and 5"""
        if not 1 <= score <= 5:
            raise ValueError("Rating must be between 1 and 5")
        return score
    
    def to_dict(self):
        """Convert rating to dictionary"""
        return {
            'id': str(self.id),
            'score': self.score,
            'review': self.review,
            'user_id': str(self.user_id),
            'recipe_id': str(self.recipe_id),
            'created_at': self.created_at.isoformat(),
            'user': self.user.to_dict() if self.user else None
        }    