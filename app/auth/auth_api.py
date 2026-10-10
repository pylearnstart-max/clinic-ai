
from flask import Blueprint, jsonify, request

from app.auth.auth_service import AuthService

auth_api = Blueprint("auth_api", __name__, url_prefix="/api/auth")
auth_service = AuthService()


@auth_api.route("/register", methods=["POST"])
def register():
    data = request.get_json(silent=True)

    if not isinstance(data, dict):
        return jsonify({
            "error": "Request body must be a JSON object"
        }), 400

    try:
        result = auth_service.register(
            email=data.get("email"),
            password=data.get("password"),
        )

        return jsonify({
            "message": "User registered successfully",
            "user": result,
        }), 201

    except ValueError as error:
        return jsonify({"error": str(error)}), 400

    except RuntimeError:
        return jsonify({
            "error": "Authentication service is not configured"
        }), 500


@auth_api.route("/login", methods=["POST"])
def login():
    data = request.get_json(silent=True)

    if not isinstance(data, dict):
        return jsonify({
            "error": "Request body must be a JSON object"
        }), 400

    try:
        result = auth_service.login(
            email=data.get("email"),
            password=data.get("password"),
        )

        return jsonify(result), 200

    except ValueError as error:
        return jsonify({"error": str(error)}), 401

    except RuntimeError:
        return jsonify({
            "error": "Authentication service is not configured"
        }), 500