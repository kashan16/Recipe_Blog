from datetime import datetime
import uuid
from sqlalchemy.dialects.postgresql import UUID, JSON
from . import db

class AuditLog(db.Model):
    """Track all important changes for security and debugging"""
    __tablename__ = "audit_logs"
    
    user_id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    action = db.Column(db.String(50), nullable=False)
    table_name = db.Column(db.String(50), nullable=False)
    record_id = db.Column(UUID(as_uuid=True), nullable=False)
    changes = db.Column(JSON)
    ip_address = db.Column(db.String(45))
    user_agent = db.Column(db.String(500))
        
    def to_dict(self):
        """Convert audit log to dictionary"""
        return {
            'id': str(self.id),
            'user_id': str(self.user_id) if self.user_id else None,
            'action': self.action,
            'table_name': self.table_name,
            'record_id': str(self.record_id),
            'changes': self.changes,
            'ip_address': self.ip_address,
            'user_agent': self.user_agent,
            'created_at': self.created_at.isoformat()
        }
    