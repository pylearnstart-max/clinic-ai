
import pytest
from flask import Flask, jsonify

import app.auth.auth_decorator as auth_decorator
from app.auth.auth_decorator import require_role


@pytest.fixture
def client(monkeypatch):
    app = Flask(__name__)

    @app.route("/admin")
    @require_role("admin")
    def admin_route():
        return jsonify({"message": "Admin access granted"}), 200

    def fake_verify_token(token):
        if token == "user-token":
            return {"user_id": 1, "role": "user"}

        if token == "admin-token":
            return {"user_id": 2, "role": "admin"}

        raise ValueError("Invalid token")

    monkeypatch.setattr(
        auth_decorator.auth_service,
        "verify_token",
        fake_verify_token,
    )

    return app.test_client()


def test_role_required_without_token_returns_401(client):
    response = client.get("/admin")

    assert response.status_code == 401


def test_user_role_cannot_access_admin_route(client):
    response = client.get(
        "/admin",
        headers={"Authorization": "Bearer user-token"}
    )

    assert response.status_code == 403


def test_admin_role_can_access_admin_route(client):
    response = client.get(
        "/admin",
        headers={"Authorization": "Bearer admin-token"}
    )

    assert response.status_code == 200
    assert response.get_json()["message"] == "Admin access granted"


def test_invalid_token_returns_401(client):
    response = client.get(
        "/admin",
        headers={"Authorization": "Bearer invalid-token"}
    )

    assert response.status_code == 401
    assert response.get_json()["error"] == "Invalid token"
