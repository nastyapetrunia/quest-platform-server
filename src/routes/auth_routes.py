from flask import request
from pydantic import BaseModel, ValidationError
from flask_restx import Namespace, Resource, fields

from src.utils.exceptions import *
from src.utils.helpers import format_payload_validation_errors
from src.services.auth import signup_with_email, login_with_email

auth_ns = Namespace("auth", description="User Authentication")

signup_response_model = auth_ns.model('SignupResponse', {
    "token": fields.String(description="JWT token for the authenticated user")
})

login_response_model = auth_ns.model('LoginResponse', {
    "token": fields.String(description="JWT token for the authenticated user")
})

error_response_model = auth_ns.model('ErrorResponse', {
    "error": fields.String(description="Error message")
})

signup_with_email_model = auth_ns.model('SignupWithEmail', {
    "name": fields.String(required=True, description='User name'),
    "email": fields.String(required=True, description='User email'),
    'password': fields.String(required=True, description='User password')
})

login_with_email_model = auth_ns.model('LoginWithEmail', {
    "email": fields.String(required=True, description='User email'),
    'password': fields.String(required=True, description='User password')
})

#TODO: add validation rules, remove from main
class SignupWithEmailPayload(BaseModel):
    name: str
    email: str
    password: str

    class Config:
        extra = 'forbid'

class LoginWithEmailPayload(BaseModel):
    email: str
    password: str

    class Config:
        extra = 'forbid'

@auth_ns.route("/signup/email")
class SignupWithEmail(Resource):
    @auth_ns.expect(signup_with_email_model)
    @auth_ns.response(201, 'User successfully created', signup_response_model)
    @auth_ns.response(400, 'Bad Request', error_response_model)
    @auth_ns.response(500, 'Internal Server Error', error_response_model)
    def post(self):
        data = request.get_json()
        try:
            SignupWithEmailPayload(**data)
        except ValidationError as e:
            return {"error": format_payload_validation_errors(e.errors())}, 400

        try:
            token = signup_with_email(data=data)
            return {"token": token}, 201
        except (EmailInUse, ValueError, DocumentValidationError, InvalidEmail) as e:
            return {"error": str(e)}, 400
        except (DatabaseConnectionError, InsertionError, Exception) as e:
            return {"error": str(e)}, 500

@auth_ns.route("/login/email")
class LoginWithEmail(Resource):
    @auth_ns.expect(login_with_email_model)
    @auth_ns.response(200, 'Login successful', login_response_model)
    @auth_ns.response(400, 'Bad Request', error_response_model)
    @auth_ns.response(401, 'Unauthorized - Wrong email or password', error_response_model)
    @auth_ns.response(500, 'Internal Server Error', error_response_model)
    def post(self):
        data = request.get_json()
        try:
            LoginWithEmailPayload(**data)
        except ValidationError as e:
            return {"error": format_payload_validation_errors(e.errors())}, 400

        try:
            token = login_with_email(data=data)
            return {"token": token}, 200
        except ValueError as e:
            return {"error": str(e)}, 400
        except WrongEmailOrPassword as e:
            return {"error": str(e)}, 401
        except Exception as e:
            return {"error": str(e)}, 500
