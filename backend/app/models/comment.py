from datetime import datetime
import uuid
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import validates
from . import db

class Comment(db.Model):
    __tablename__ = "comments"
    
    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    content = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    is_edited = db.Column(db.Boolean, default=False)
    edited_at = db.Column(db.DateTime)
    
    user_id = db.Column(UUID(as_uuid=True), db.ForeignKey("users.id"), nullable=False)
    recipe_id = db.Column(UUID(as_uuid=True), db.ForeignKey("recipes.id"), nullable=False)
    parent_id = db.Column(UUID(as_uuid=True), db.ForeignKey("comments.id"))
    
    replies = db.relationship("Comment", backref=db.backref("parent", remote_side="Comment.id"))
    
    @validates('content')
    def validate_content(self, key, content):
        """Validate comment content"""
        if len(content.strip()) < 1:
            raise ValueError("Comment cannot be empty")
        if len(content) > 1000:
            raise ValueError("Comment too long (max 1000 characters)")
        return content.strip()
    
    def to_dict(self, include_replies=False):
        """Convert comment to dictionary"""
        data = {
            'id': str(self.id),
            'content': self.content,
            'is_edited': self.is_edited,
            'edited_at': self.edited_at.isoformat() if self.edited_at else None,
            'user_id': str(self.user_id),
            'recipe_id': str(self.recipe_id),
            'parent_id': str(self.parent_id) if self.parent_id else None,
            'created_at': self.created_at.isoformat(),
            'user': self.user.to_dict() if self.user else None
        }
        
        if include_replies:
            data['replies'] = [reply.to_dict() for reply in self.replies]
        
        return data    
    