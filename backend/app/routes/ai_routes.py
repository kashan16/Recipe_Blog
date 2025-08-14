from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
import os
import requests

ai_bp = Blueprint("ai", __name__)

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
GEMINI_MODEL = "gemini-1.5-flash"

def generate_recipe_idea(prompt: str) -> str:
    """
    Calls Google Gemini API to generate a recipe idea based on the given prompt.
    """
    if not GEMINI_API_KEY:
        raise ValueError("GEMINI_API_KEY not set in environment variables.")

    url = f"https://generativelanguage.googleapis.com/v1beta/models/{GEMINI_MODEL}:generateContent?key={GEMINI_API_KEY}"

    headers = {"Content-Type": "application/json"}
    payload = {
        "contents": [
            {
                "parts": [{"text": prompt}]
            }
        ]
    }

    response = requests.post(url, headers=headers, json=payload)

    if response.status_code != 200:
        raise RuntimeError(f"Gemini API error: {response.status_code} - {response.text}")

    data = response.json()

    try:
        return data["candidates"][0]["content"]["parts"][0]["text"]
    except (KeyError, IndexError):
        raise ValueError("Unexpected response format from Gemini API.")

@ai_bp.route("/generate", methods=["POST"])
@jwt_required()
def generate_recipe():
    data = request.get_json()
    prompt = data.get("prompt")
    if not prompt:
        return jsonify({"error": "Prompt required"}), 400
    try:
        result = generate_recipe_idea(prompt)
        return jsonify({"recipe": result})
    except Exception as e:
        return jsonify({"error": str(e)}), 500
