from datetime import datetime
import uuid
from sqlalchemy.dialects.postgresql import UUID
from . import db
from sqlalchemy.orm import validates


class AIRequest(db.Model):
    __tablename__ = "ai_requests"
    
    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    prompt = db.Column(db.Text, nullable=False)
    response = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    model_used = db.Column(db.String(50))
    token_used = db.Column(db.Integer)
    cost = db.Column(db.Float)
    status = db.Column(db.String(20), default="pending")
    error_message = db.Column(db.Text)
    
    user_id = db.Column(UUID(as_uuid=True), db.ForeignKey("users.id"), nullable=False)
    
    @validates('status')
    def validate_status(self, key, status):
        """Validate AI request status"""
        allowed_statuses = ['pending', 'completed', 'failed', 'timeout']
        if status not in allowed_statuses:
            raise ValueError(f"Status must be one of: {', '.join(allowed_statuses)}")
        return status
    
    def to_dict(self):
        """Convert AI request to dictionary"""
        return {
            'id': str(self.id),
            'prompt': self.prompt,
            'response': self.response,
            'model_used': self.model_used,
            'tokens_used': self.tokens_used,
            'cost': self.cost,
            'status': self.status,
            'error_message': self.error_message,
            'user_id': str(self.user_id),
            'created_at': self.created_at.isoformat()
        }    