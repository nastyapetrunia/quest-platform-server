import os
import re
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

def validate_email(user_email):
    """
    Validates an email address using regex pattern matching and basic checks.
    Returns (bool, str) tuple with validation result and error message.
    """
    if not isinstance(user_email, str):
        return False, "Email must be a string"

    if not user_email:
        return False, "Email cannot be empty"

    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'

    if not re.match(pattern, user_email):
        return False, "Invalid email format"

    if len(user_email) > 254:
        return False, "Email too long"

    if user_email.count('@') != 1:
        return False, "Email must contain exactly one @ symbol"

    local_part = user_email.split('@')[0]
    if len(local_part) > 64:
        return False, "Local part too long"

    return True, "Valid email"
