from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from sqlalchemy import desc
from extensions import gemini_client, db
from models.ai_request import AIRequest
from utils.decorators import premium_required
from utils.helpers import log_audit_event

ai_bp = Blueprint('ai', __name__)

@ai_bp.route('/generate-recipe', methods=['POST'])
@premium_required
def generate_recipe():
    """Generate a recipe using Google Gemini (Premium feature)"""
    current_user_id = get_jwt_identity()
    data = request.get_json()
    prompt = data.get('prompt', '').strip()

    if not prompt:
        return jsonify({'error': 'Prompt is required'}), 400

    # Create AI request record
    ai_request = AIRequest(
        prompt=prompt,
        model_used="gemini-pro",
        user_id=current_user_id
    )

    try:
        db.session.add(ai_request)
        db.session.flush()  # Get the ID

        # Google Gemini API call
        response = gemini_client.generate_content(
            f"You are a professional chef assistant. Create a detailed recipe for: {prompt}. "
            f"Include ingredients, instructions, prep time, cook time, difficulty level."
        )

        # Gemini returns a `text` property for the result
        ai_response = response.text if hasattr(response, "text") else str(response)

        ai_request.response = ai_response
        ai_request.status = 'completed'
        # Google doesn’t provide token usage or cost directly
        ai_request.tokens_used = None
        ai_request.cost = None

        db.session.commit()

        # Log AI usage
        log_audit_event(
            user_id=current_user_id,
            action='AI_REQUEST',
            table_name='ai_requests',
            record_id=ai_request.id,
            ip_address=request.remote_addr
        )

        return jsonify({
            'message': 'Recipe generated successfully',
            'response': ai_response,
            'request_details': ai_request.to_dict()
        }), 200

    except Exception as e:
        ai_request.status = 'failed'
        ai_request.error_message = str(e)
        db.session.commit()

        return jsonify({'error': 'AI request failed', 'details': str(e)}), 500


@ai_bp.route('/my-requests', methods=['GET'])
@jwt_required()
def get_my_ai_requests():
    """Get current user's AI requests"""
    current_user_id = get_jwt_identity()
    page = request.args.get('page', 1, type=int)
    per_page = min(request.args.get('per_page', 10, type=int), 50)

    requests = AIRequest.query.filter_by(user_id=current_user_id).order_by(
        desc(AIRequest.created_at)
    ).paginate(page=page, per_page=per_page, error_out=False)

    return jsonify({
        'requests': [req.to_dict() for req in requests.items],
        'pagination': {
            'page': page,
            'pages': requests.pages,
            'per_page': per_page,
            'total': requests.total,
            'has_next': requests.has_next,
            'has_prev': requests.has_prev
        }
    }), 200
