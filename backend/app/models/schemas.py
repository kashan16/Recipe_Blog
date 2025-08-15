from marshmallow import Schema, fields, validate, validates, ValidationError
from marshmallow_sqlalchemy import SQLAlchemyAutoSchema
from .user import User
from .recipe import Recipe
from .comment import Comment
from .ratings import Rating
from .payment import Payment

class UserRegistrationSchema(Schema) :
    """Schema for user registration"""
    username = fields.Str(required=True, validate=validate.Length(min=3,max=80))
    email = fields.Email(required=True)
    password = fields.Str(required=True, validate=validate.Length(min=8))
    first_name = fields.Str(validate=validate.Length(max=50))
    last_name = fields.Str(validate=validate.Length(max=50))
    
    
class UserLoginSchema(Schema) :
    """Schema for user login"""
    email = fields.Email(required=True)
    password = fields.Str(required=True)


class RecipeCreateSchema(Schema):
    """Schema for creating recipes"""
    title = fields.Str(required=True, validate=validate.Length(min=1, max=150))
    description = fields.Str(required=True)
    ingredients = fields.Str(required=True)
    instructions = fields.Str(required=True)
    prep_time = fields.Int(validate=validate.Range(min=1))
    cook_time = fields.Int(validate=validate.Range(min=1))
    servings = fields.Int(validate=validate.Range(min=1))
    difficulty_level = fields.Str(validate=validate.OneOf(['easy', 'medium', 'hard']))
    tags = fields.List(fields.Str(), missing=[])


class RecipeUpdateSchema(RecipeCreateSchema):
    """Schema for updating recipes - all fields optional"""
    title = fields.Str(validate=validate.Length(min=1, max=150))
    description = fields.Str()
    ingredients = fields.Str()
    instructions = fields.Str()


class CommentCreateSchema(Schema):
    """Schema for creating comments"""
    content = fields.Str(required=True, validate=validate.Length(min=1, max=1000))
    parent_id = fields.UUID()


class RatingCreateSchema(Schema):
    """Schema for creating ratings"""
    score = fields.Int(required=True, validate=validate.Range(min=1, max=5))
    review = fields.Str(validate=validate.Length(max=500))


class PaymentCreateSchema(Schema):
    """Schema for creating payments"""
    amount = fields.Float(required=True, validate=validate.Range(min=0.01))
    currency = fields.Str(missing='INR', validate=validate.OneOf(['INR', 'USD', 'EUR']))
    payment_method = fields.Str(validate=validate.OneOf(['card', 'upi', 'netbanking', 'wallet']))
    description = fields.Str(validate=validate.Length(max=200))

    