import os
import re
import jwt
import datetime
from functools import wraps
from dotenv import load_dotenv
from flask import request, abort

load_dotenv()

JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY")

def generate_jwt_token(user_id: str) -> str:
    """Generate JWT Token for a user."""
    expiration = datetime.datetime.now(datetime.UTC) + datetime.timedelta(days=1)  # Token valid for 1 day
    payload = {
        "sub": user_id,
        "exp": expiration
    }
    token = jwt.encode(payload, JWT_SECRET_KEY, algorithm="HS256")
    return token

def format_payload_validation_errors(errors):
    error_messages = []

    for error in errors:
        field = ".".join(error["loc"])
        error_type = error["type"]
        message = error["msg"]

        if "required" in error_type:
            error_message = f"Field '{field}' is required."
        elif "type_error" in error_type:
            expected_type = error_type.split(".")[-1]
            error_message = f"Field '{field}' must be of type {expected_type}."
        elif "value_error" in error_type:
            error_message = f"Field '{field}' has an invalid value: {message}."
        else:
            error_message = f"Field '{field}' has an error: {message}."

        error_messages.append(error_message)

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

def token_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        token = None
        if 'Authorization' in request.headers:
            token = request.headers['Authorization'].split(" ")[1]  # Get token from "Bearer <token>"

        if not token:
            abort(401, "Token is missing")

        try:
            # Verify the token and decode it
            payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=["HS256"])
            # Optionally, you can store the payload in the request context for later use
            request.user_id = payload['sub']  # Assuming 'sub' is the user ID in the JWT
        except jwt.ExpiredSignatureError:
            abort(401, "Token has expired")
        except jwt.InvalidTokenError:
            abort(401, "Invalid token")

        return f(*args, **kwargs)

    return decorated_function
