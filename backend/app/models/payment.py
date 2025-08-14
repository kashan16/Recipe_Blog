from datetime import datetime
import uuid
from sqlalchemy.dialects.postgresql import UUID
from . import db
from sqlalchemy.orm import validates

class Payment(db.Model):
    __tablename__ = "payments"
    
    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    amount = db.Column(db.Float, nullable=False)
    currency = db.Column(db.String(10), default="INR")
    status = db.Column(db.String(20), default="pending")
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    payment_id = db.Column(db.String(50))
    payment_method = db.Column(db.String(50)) # card , upi , wallet etc.
    description = db.Column(db.String(200))
    failure_reason = db.Column(db.String(200))
    
    user_id = db.Column(UUID(as_uuid=True), db.ForeignKey("users.id"), nullable=False)
    
    @validates('status')
    def validate_status(self, key, status):
        """Validate payment status"""
        allowed_statuses = ['pending', 'completed', 'failed', 'refunded', 'cancelled']
        if status not in allowed_statuses:
            raise ValueError(f"Status must be one of: {', '.join(allowed_statuses)}")
        return status
    
    @validates('amount')
    def validate_amount(self, key, amount):
        """Validate amount is positive"""
        if amount <= 0:
            raise ValueError("Amount must be positive")
        return amount
    
    def to_dict(self):
        """Convert payment to dictionary"""
        return {
            'id': str(self.id),
            'amount': self.amount,
            'currency': self.currency,
            'status': self.status,
            'payment_id': self.payment_id,
            'payment_method': self.payment_method,
            'description': self.description,
            'failure_reason': self.failure_reason,
            'user_id': str(self.user_id),
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
    
    
    