from flask_restx import Namespace, Resource, fields
from flask import request
from pydantic import BaseModel, ValidationError
from src.utils.helpers import format_payload_validation_errors
from src.utils.exceptions import EmailInUse, InsertionError, DatabaseConnectionError, DocumentValidationError, InvalidEmail
from src.services.auth import signup_with_email


auth_ns = Namespace("auth", description="User Authentication")

signup_with_email_model = auth_ns.model('SignupWithEmail', {
    "name": fields.String(required=True, description='User name'),
    "email": fields.String(required=True, description='User email'),
    'password': fields.String(required=True, description='User password')
})

# TODO: add validation rules, remove from main
class SignupWithEmailPayload(BaseModel):
    name: str
    email: str
    password: str

@auth_ns.route("/signup/email")
class SignupWithEmail(Resource):
    @auth_ns.expect(signup_with_email_model)
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