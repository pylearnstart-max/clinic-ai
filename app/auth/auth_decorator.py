
from functools import wraps

from flask import jsonify, request

from app.auth.auth_service import AuthService


auth_service = AuthService()


def require_auth(view_function):

    @wraps(view_function)
    def decorated_function(*args, **kwargs):

        auth_header = request.headers.get("Authorization", "")
        parts = auth_header.split()

        if len(parts) != 2 or parts[0].lower() != "bearer":
            return jsonify({
                "error": "Bearer token is required"
            }), 401

        token = parts[1]

        try:
            current_user = auth_service.verify_token(token)

        except ValueError as error:
            return jsonify({
                "error": str(error)
            }), 401

        except RuntimeError:
            return jsonify({
                "error": "Authentication service is not configured"
            }), 500

        request.current_user = current_user

        return view_function(*args, **kwargs)

    return decorated_function


def require_role(*allowed_roles):

    def decorator(view_function):

        @wraps(view_function)
        @require_auth
        def decorated_function(*args, **kwargs):

            current_user = request.current_user
            user_role = current_user.get("role")

            if user_role not in allowed_roles:
                return jsonify({
                    "error": "You do not have permission to access this resource"
                }), 403

            return view_function(*args, **kwargs)

        return decorated_function

    return decorator