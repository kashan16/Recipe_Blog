import razorpay
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from config import Config
from models import Payment, db
import razorpay.errors

payment_bp = Blueprint("payments",__name__)
client = razorpay.Client(auth=(Config.RAZORPAY_KEY_ID,Config.RAZORPAY_KEY_SECRET))

@payment_bp.route("/create_order",methods=["POST"])
@jwt_required()
def create_order():
    data = request.get_json()
    amount = int(data["amount"]) * 100
    order = client.order.create({"amount" : amount , "currency" : "INR" , "payment_capture" : "1"})
    return jsonify(order)

@payment_bp.route("/verify",methods=["POST"])
@jwt_required()
def verify_payment():
    data = request.get_json()
    try :
        client.utility.verify_payment_signature(data)
        payment = Payment(
            user_id=get_jwt_identity(),
            order_id=data["razorpay_order_id"],
            payment_id=data["razorpay_payment_id"]
        )
        db.session.add(payment)
        db.commit()
        return jsonify({"message" : "Payment verified successfully"})
    except razorpay.errors.SignatureVerificationError:
        return jsonify({"error" : "Payment verification failed"}), 400