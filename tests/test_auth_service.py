from datetime import datetime, timedelta, timezone

import jwt
import pytest

from app.auth.auth_service import AuthService


def test_verify_token_rejects_expired_token():
    service = AuthService()
    service.secret_key = "test-secret-key"

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
