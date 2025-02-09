import os
import re
import jwt
import uuid
import boto3
import datetime
import mimetypes
from functools import wraps
from dotenv import load_dotenv
from flask import request, abort
from flask import Flask, request, jsonify

load_dotenv()

S3_BUCKET_RESOURCES = os.getenv("S3_BUCKET_RESOURCES")
S3_REGION = os.getenv("S3_REGION")
S3_ACCESS_KEY = os.getenv("AWS_ACCESS_KEY_ID")
S3_SECRET_KEY = os.getenv("AWS_SECRET_ACCESS_KEY")
CLOUDFRONT_DISTRIBUTION = os.getenv("CLOUDFRONT_DISTRIBUTION")

s3_client = boto3.client(
    "s3",
    aws_access_key_id=S3_ACCESS_KEY,
    aws_secret_access_key=S3_SECRET_KEY,
    region_name=S3_REGION,
)

JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY")

def generate_unique_filename(filename):
    """Generate a unique filename using UUID and keep the original extension."""
    ext = os.path.splitext(filename)[1]
    return f"{uuid.uuid4().hex}{ext}"

def upload_to_s3(file):
    unique_filename = generate_unique_filename(file.filename)

    content_type, _ = mimetypes.guess_type(file.filename)
    content_type = content_type or 'application/octet-stream'

    s3_client.upload_fileobj(
        file, S3_BUCKET_RESOURCES, unique_filename, ExtraArgs={"ContentType": content_type}
    )
    return f"{CLOUDFRONT_DISTRIBUTION}/{unique_filename}"


def generate_jwt_token(user_id: str) -> str:
    """Generate JWT Token for a user."""
    expiration = datetime.datetime.now(datetime.UTC) + datetime.timedelta(days=1)
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
            token = request.headers['Authorization'].split(" ")[1]

        if not token:
            abort(401, "Token is missing")

        try:
            payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=["HS256"])
            request.user_id = payload['sub']
        except jwt.ExpiredSignatureError:
            abort(401, "Token has expired")
        except jwt.InvalidTokenError:
            abort(401, "Invalid token")

        return f(*args, **kwargs)

    return decorated_function
