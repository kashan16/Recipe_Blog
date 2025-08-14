from datetime import datetime
from . import db
import uuid
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import validates
from werkzeug.security import generate_password_hash, check_password_hash

class User(db.Model):
    __tablename__ = "users"
        
    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    updated_at = db.Column(db.DateTime, onupdate=datetime.utcnow)
    is_deleted = db.Column(db.Boolean, default=False)
    username = db.Column(db.String(80), unique=True, nullable=False, index=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(128), nullable=False)
    is_premium = db.Column(db.Boolean, default=False)
    first_name = db.Column(db.String(50))
    last_name = db.Column(db.String(50))
    bio = db.Column(db.Text)
    profile_image_url = db.Column(db.String(255))
    last_login = db.Column(db.DateTime)
    is_active = db.Column(db.Boolean, default=True)
    
    recipes = db.relationship("Recipe", backref="author", lazy=True)
    comments = db.relationship("Comment", backref="user", lazy=True)
    ratings = db.relationship("Rating", backref="user", lazy=True)
    payments = db.relationship("Payment", backref="user", lazy=True)
    ai_request = db.relationship("AIRequest", backref="user", lazy=True)
    
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
        
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    @validates('email')
    def validate_email(self, key, email):
        """Basic email Validation"""
        #MAKE SURE TO VALIDATE EMAIL ON THE FRONTEND
        if '@' not in email:
            raise ValueError("Invalid email address")
        return email.lower()
    
    @validates('username')
    def validate_username(self, key, username):
        """Basic username validation"""
        #MAKE SURE TO VALIDATE ON THE FRONTEND
        if len(username) < 3:
            raise ValueError("Username must be atleast 3 characters long")
        return username.lower()
    
    def to_dict(self, include_sensitive=False):
        """Convert user to dictionary"""
        data = {
            'id' : str(self.id),
            'username' : self.username,
            'email' : self.email if include_sensitive else None,
            'is_premium' : self.is_premium,
            'first_name' : self.first_name,
            'last_name' : self.last_name,
            'bio' : self.bio,
            'profile_image_url' : self.profile_image_url,
            'created_at' : self.created_at.isoformat(),
            'is_active' : self.is_active
        }
        return data
        
    def __repr__(self):
        return f"<User {self.username}>"
    