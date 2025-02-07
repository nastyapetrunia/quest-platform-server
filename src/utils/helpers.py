import os
import jwt
import datetime

SECRET_KEY = os.getenv("JWT_SECRET_KEY")

def generate_jwt_token(user_id: str) -> str:
    """Generate JWT Token for a user."""
    expiration = datetime.datetime.now(datetime.UTC) + datetime.timedelta(days=1)  # Token valid for 1 day
    payload = {
        "sub": user_id,
        "exp": expiration
    }
    token = jwt.encode(payload, SECRET_KEY, algorithm="HS256")
    return token

def format_payload_validation_errors(errors):
    error_messages = []

    for error in errors:
        field = ".".join(error["loc"])
        message = f"Field '{field}' is required."

        error_messages.append(message)

    return "\n".join(error_messages)