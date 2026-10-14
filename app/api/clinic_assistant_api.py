
from flask import Blueprint, current_app, jsonify, request

from app.auth.auth_decorator import require_auth
from app.ai.rag_service import ClinicRAGService
from app.services.clinic_assistant_service import ClinicAssistantService


clinic_assistant_api = Blueprint(
    "clinic_assistant_api",
    __name__,
    url_prefix="/api"
)

assistant_service = ClinicAssistantService()
rag_service = ClinicRAGService()


@clinic_assistant_api.route("/assistant/chat", methods=["POST"])
@require_auth
def chat_with_assistant():
    data = request.get_json(silent=True)

    if not isinstance(data, dict):
        return jsonify({
            "error": "Request body must be a JSON object"
        }), 400

    message = data.get("message")

    if not isinstance(message, str) or not message.strip():
        return jsonify({
            "error": "Message is required"
        }), 400

    try:
        response = assistant_service.get_response(message)

        return jsonify({
            "response": response
        }), 200

    except ValueError as error:
        return jsonify({
            "error": str(error)
        }), 400

    except Exception:
        current_app.logger.exception(
            "Unexpected error in Clinic Assistant API"
        )

        return jsonify({
            "error": "Internal server error"
        }), 500


@clinic_assistant_api.route("/ai/ask", methods=["POST"])
@require_auth
def ask_clinic_rag():
    data = request.get_json(silent=True)

    # Validate request body
    if not isinstance(data, dict):
        return jsonify({
            "error": "Request body must be a JSON object"
        }), 400

    # Validate question
    question = data.get("question")

    if not isinstance(question, str) or not question.strip():
        return jsonify({
            "error": "Question is required"
        }), 400

    try:
        answer = rag_service.answer_question(question)

        return jsonify({
            "question": question.strip(),
            "answer": answer
        }), 200

    except ValueError as error:
        return jsonify({
            "error": str(error)
        }), 400

    except Exception:
        current_app.logger.exception(
            "Unexpected error in ClinicAI RAG API"
        )

        return jsonify({
            "error": "Internal server error"
        }), 500
