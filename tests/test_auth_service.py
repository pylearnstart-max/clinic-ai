from datetime import datetime, timedelta, timezone

import jwt
import pytest

from app.auth.auth_service import AuthService


def test_verify_token_rejects_expired_token():
    service = AuthService()
    service.secret_key = "test-secret-key-for-jwt-32-bytes-minimum"

    now = datetime.now(timezone.utc)

    payload = {
        "sub": "1",
        "role": "user",
        "iat": now - timedelta(hours=1),
        "exp": now - timedelta(minutes=1),
    }

    token = jwt.encode(
        payload,
        service.secret_key,
        algorithm="HS256",
    )

    with pytest.raises(ValueError, match="Token has expired"):
        service.verify_token(token)


def test_verify_token_rejects_invalid_signature():
    service = AuthService()
    service.secret_key = "correct-test-secret-for-jwt-32-bytes"

    payload = {
        "sub": "1",
        "role": "user",
        "iat": datetime.now(timezone.utc),
        "exp": datetime.now(timezone.utc) + timedelta(minutes=5),
    }

    token = jwt.encode(
        payload,
        "wrong-test-secret-for-jwt-32-bytes",
        algorithm="HS256",
    )

    with pytest.raises(ValueError, match="Invalid token"):
        service.verify_token(token)



@pytest.mark.parametrize("missing_claim", ["sub", "role", "iat", "exp"])
def test_verify_token_rejects_missing_required_claim(missing_claim):
    service = AuthService()
    service.secret_key = "test-secret-key-for-jwt-32-bytes-minimum"

    now = datetime.now(timezone.utc)

    payload = {
        "sub": "1",
        "role": "user",
        "iat": now,
        "exp": now + timedelta(minutes=5),
    }

    payload.pop(missing_claim)

    token = jwt.encode(
        payload,
        service.secret_key,
        algorithm="HS256",
    )

    with pytest.raises(ValueError, match="Invalid token"):
        service.verify_token(token)


@pytest.mark.parametrize("claim_name", ["sub", "role"])
def test_verify_token_rejects_empty_claim_value(claim_name):
    service = AuthService()
    service.secret_key = "test-secret-key-for-jwt-32-bytes-minimum"

    now = datetime.now(timezone.utc)

    payload = {
        "sub": "1",
        "role": "user",
        "iat": now,
        "exp": now + timedelta(minutes=5),
    }

    payload[claim_name] = "   " if claim_name == "sub" else ""

    token = jwt.encode(
        payload,
        service.secret_key,
        algorithm="HS256",
    )

    with pytest.raises(ValueError, match="Invalid token"):
        service.verify_token(token)

def test_verify_token_rejects_missing_token():
    service = AuthService()
    service.secret_key = "test-secret-key-for-jwt-32-bytes-minimum"

    with pytest.raises(ValueError, match="Token is required"):
        service.verify_token("")

def test_verify_token_rejects_missing_secret_key():
    service = AuthService()
    service.secret_key = None

    with pytest.raises(
        RuntimeError,
        match="JWT_SECRET_KEY is not configured",
    ):
        service.verify_token("some-token")
