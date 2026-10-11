
from flask import Blueprint, current_app, jsonify, request

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

    # Validate request body
    if not isinstance(data, dict):
        return jsonify({
            "error": "Request body must be a JSON object"
        }), 400

    # Validate message
    message = data.get("message")

    if not isinstance(message, str) or not message.strip():
        return jsonify({
            "error": "Message is required"
        }), 400

    try:
        # Get response from assistant service
        response = assistant_service.get_response(message)

        return jsonify({
            "response": response
        }), 200

    except ValueError as error:
        # Handle expected validation errors
        return jsonify({
            "error": str(error)
        }), 400

    except Exception:
        # Log unexpected errors for debugging
        current_app.logger.exception(
            "Unexpected error in Clinic Assistant API"
        )

        # Return a safe message to the client
        return jsonify({
            "error": "Internal server error"
        }), 500