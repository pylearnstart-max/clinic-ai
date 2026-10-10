
import os
from datetime import datetime, timedelta, timezone

import jwt
from dotenv import load_dotenv
from werkzeug.security import (
    generate_password_hash,
    check_password_hash,
)

from app.auth.user_repository import UserRepository


# Load environment variables from .env
load_dotenv()


class AuthService:

    def __init__(self):
        self.user_repository = UserRepository()
        self.secret_key = os.getenv("JWT_SECRET_KEY")

    # Register a new user
    def register(self, email, password):

        if not isinstance(email, str) or not email.strip():
            raise ValueError("Email is required")

        if not isinstance(password, str) or len(password) < 8:
            raise ValueError(
                "Password must be at least 8 characters"
            )

        email = email.strip().lower()

        existing_user = self.user_repository.get_by_email(email)

        if existing_user:
            raise ValueError("Email is already registered")

        password_hash = generate_password_hash(password)

        user_id = self.user_repository.create_user(
            email=email,
            password_hash=password_hash,
        )

        return {
            "user_id": user_id,
            "email": email,
        }

    # Login an existing user
    def login(self, email, password):

        if (
            not isinstance(email, str)
            or not email.strip()
            or not isinstance(password, str)
            or not password
        ):
            raise ValueError("Email and password are required")

        user = self.user_repository.get_by_email(
            email.strip().lower()
        )

        if user is None or not check_password_hash(
            user["password_hash"], password
        ):
            raise ValueError("Invalid email or password")

        if not self.secret_key:
            raise RuntimeError(
                "JWT_SECRET_KEY is not configured"
            )

        now = datetime.now(timezone.utc)

        payload = {
            "sub": str(user["user_id"]),
            "role": user["role"],
            "iat": now,
            "exp": now + timedelta(minutes=30),
        }

        token = jwt.encode(
            payload,
            self.secret_key,
            algorithm="HS256",
        )

        return {
            "access_token": token,
            "token_type": "Bearer",
        }

    # Verify a JWT token
    def verify_token(self, token):

        if not token or not isinstance(token, str):
            raise ValueError("Token is required")

        if not self.secret_key:
            raise RuntimeError(
                "JWT_SECRET_KEY is not configured"
            )

        try:
            payload = jwt.decode(
                token,
                self.secret_key,
                algorithms=["HS256"],
                options={
                    "require": ["sub", "role", "iat", "exp"]
                },
            )

            user_id = payload.get("sub")
            role = payload.get("role")

            if (
                not isinstance(user_id, str)
                or not user_id.strip()
                or not isinstance(role, str)
                or not role.strip()
            ):
                raise ValueError("Invalid token")

            return {
                "user_id": user_id,
                "role": role,
            }

        except jwt.ExpiredSignatureError:
            raise ValueError("Token has expired")

        except jwt.InvalidTokenError:
            raise ValueError("Invalid token")