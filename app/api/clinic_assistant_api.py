from flask import Blueprint, jsonify, request

from app.auth.auth_decorator import require_auth
from app.services.clinic_assistant_service import ClinicAssistantService


clinic_assistant_api = Blueprint(
    "clinic_assistant_api",
    __name__,
    url_prefix="/api"
)

assistant_service = ClinicAssistantService()


@clinic_assistant_api.route("/assistant/chat", methods=["POST"])
@require_auth
def chat_with_assistant():
    data = request.get_json(silent=True)

    if not isinstance(data, dict):
        return jsonify({"error": "Request body must be a JSON object"}), 400

    message = data.get("message")

    if not isinstance(message, str) or not message.strip():
        return jsonify({"error": "Message is required"}), 400

    try:
        response = assistant_service.get_response(message)
        return jsonify({"response": response}), 200

    except ValueError as error:
        return jsonify({"error": str(error)}), 400

    except Exception:
        return jsonify({"error": "Internal server error"}), 500
