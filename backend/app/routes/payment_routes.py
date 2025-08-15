from datetime import datetime
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from marshmallow import ValidationError
import razorpay
import os

from models import db
from models.payment import Payment
from models.user import User
from models.schemas import PaymentCreateSchema
from sqlalchemy import desc
from utils.helpers import log_audit_event

payment_bp = Blueprint('payments', __name__)

# Initialize Razorpay client
razorpay_client = razorpay.Client(
    auth=(
        os.environ.get('RAZORPAY_KEY_ID'),
        os.environ.get('RAZORPAY_KEY_SECRET')
    )
)

@payment_bp.route('/create-order', methods=['POST'])
@jwt_required()
def create_payment_order():
    """Create a payment order"""
    current_user_id = get_jwt_identity()
    
    try:
        schema = PaymentCreateSchema()
        data = schema.load(request.get_json())
    except ValidationError as err:
        return jsonify({'error': 'Validation failed', 'details': err.messages}), 400
    
    try:
        # Create Razorpay order
        order_data = {
            'amount': int(data['amount'] * 100),  # Amount in paise
            'currency': data.get('currency', 'INR'),
            'receipt': f'receipt_{current_user_id}_{int(datetime.utcnow().timestamp())}'
        }
        
        razorpay_order = razorpay_client.order.create(data=order_data)
        
        # Create payment record
        payment = Payment(
            amount=data['amount'],
            currency=data.get('currency', 'INR'),
            payment_id=razorpay_order['id'],
            payment_method=data.get('payment_method'),
            description=data.get('description'),
            user_id=current_user_id
        )
        
        db.session.add(payment)
        db.session.commit()
        
        # Log payment creation
        log_audit_event(
            user_id=current_user_id,
            action='CREATE',
            table_name='payments',
            record_id=payment.id,
            ip_address=request.remote_addr
        )
        
        return jsonify({
            'message': 'Payment order created successfully',
            'payment': payment.to_dict(),
            'razorpay_order': razorpay_order
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Payment order creation failed', 'details': str(e)}), 500

@payment_bp.route('/verify', methods=['POST'])
@jwt_required()
def verify_payment():
    """Verify payment after completion"""
    current_user_id = get_jwt_identity()
    
    data = request.get_json()
    payment_id = data.get('payment_id')
    razorpay_payment_id = data.get('razorpay_payment_id')
    razorpay_order_id = data.get('razorpay_order_id')
    razorpay_signature = data.get('razorpay_signature')
    
    if not all([payment_id, razorpay_payment_id, razorpay_order_id, razorpay_signature]):
        return jsonify({'error': 'Missing required payment verification data'}), 400
    
    # Find payment record
    payment = Payment.query.filter_by(id=payment_id, user_id=current_user_id).first()
    if not payment:
        return jsonify({'error': 'Payment record not found'}), 404
    
    try:
        # Verify payment signature
        razorpay_client.utility.verify_payment_signature({
            'razorpay_order_id': razorpay_order_id,
            'razorpay_payment_id': razorpay_payment_id,
            'razorpay_signature': razorpay_signature
        })
        
        # Update payment status
        payment.status = 'completed'
        payment.payment_id = razorpay_payment_id
        
        # If this is a premium payment, upgrade user
        if payment.description and 'premium' in payment.description.lower():
            user = User.query.get(current_user_id)
            user.is_premium = True
        
        db.session.commit()
        
        # Log payment completion
        log_audit_event(
            user_id=current_user_id,
            action='UPDATE',
            table_name='payments',
            record_id=payment.id,
            changes={'status': 'completed'},
            ip_address=request.remote_addr
        )
        
        return jsonify({
            'message': 'Payment verified successfully',
            'payment': payment.to_dict()
        }), 200
        
    except razorpay.errors.SignatureVerificationError:
        payment.status = 'failed'
        payment.failure_reason = 'Invalid signature'
        db.session.commit()
        
        return jsonify({'error': 'Payment verification failed'}), 400
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Payment verification failed', 'details': str(e)}), 500

@payment_bp.route('/my-payments', methods=['GET'])
@jwt_required()
def get_my_payments():
    """Get current user's payment history"""
    current_user_id = get_jwt_identity()
    page = request.args.get('page', 1, type=int)
    per_page = min(request.args.get('per_page', 10, type=int), 50)
    status = request.args.get('status')
    
    query = Payment.query.filter_by(user_id=current_user_id)
    
    if status:
        query = query.filter_by(status=status)
    
    payments = query.order_by(desc(Payment.created_at)).paginate(
        page=page, per_page=per_page, error_out=False
    )
    
    return jsonify({
        'payments': [payment.to_dict() for payment in payments.items],
        'pagination': {
            'page': page,
            'pages': payments.pages,
            'per_page': per_page,
            'total': payments.total,
            'has_next': payments.has_next,
            'has_prev': payments.has_prev
        }
    }), 200
