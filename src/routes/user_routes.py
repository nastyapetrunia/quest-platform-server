from bson.errors import InvalidId

from flask import request
from pydantic import BaseModel, ValidationError
from flask_restx import Namespace, Resource, fields

from src.utils.exceptions import *
from src.services.user import get_user_by_id, update_user
from src.utils.helpers import format_payload_validation_errors, token_required

user_ns = Namespace("user", description="Endpoints for user profile management, including account details and settings.")

user_model = user_ns.model('UserInfo', {
    "_id": fields.String(description="User's unique identifier (_id) as a string"),
    "name": fields.String(description="User's name"),
    "email": fields.String(description="User's email address"),
    "created_at": fields.DateTime(description="Account creation timestamp"),
    "profile_picture": fields.String(description="Profile picture S3 URL", default=None),
    "created_quests": fields.List(fields.String, description="List of created quests"),
    "quest_history": fields.List(fields.String, description="List of quest history"),
})

# Payload model for updating user info
update_user_model = user_ns.model("UpdateUser", {
    "name": fields.String(description="New user name", required=False),
    "email": fields.String(description="New email", required=False),
    "profile_picture": fields.Raw(description="New profile picture file", required=False),
})

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

@user_ns.route("/<string:user_id>")
@user_ns.param("user_id", "The unique ID of the user")
class UserResource(Resource):
    @user_ns.response(200, "Success", user_model)
    @user_ns.response(404, "User not found")
    @user_ns.response(401, "Unauthorized")
    @token_required
    def get(self, user_id):
        """Retrieve user information by ID"""
        try:
            user = get_user_by_id(user_id)
            return {"user": user}, 200
        except (ValueError, InvalidId) as e:
            return {"error": str(e)}, 400
        except NotFoundError as e:
            return {"error": str(e)}, 404
        except Exception as e:
            return {"error": str(e)}, 500

    @user_ns.expect(update_user_model)
    @user_ns.response(200, "User updated successfully")
    @user_ns.response(400, "Invalid data")
    @user_ns.response(404, "User not found")
    @user_ns.response(401, "Unauthorized")
    @token_required
    def patch(self, user_id):
        """Update user information by ID"""
        if user_id != request.user_id:
            return {"error": "Unauthorized access"}, 401

        name = request.form.get('name')
        email = request.form.get('email')
        profile_picture = request.files.get('profile_picture')

        data = {
            "name": name,
            "email": email,
            "profile_picture": profile_picture
        }

        data = {key: value for key, value in data.items() if value is not None}

        try:
            result = update_user(user_id=user_id, data=data)
            return result, 200
        except (ValueError, DocumentValidationError, UpdateError, InvalidId) as e:
            return {"error": str(e)}, 400
        except NotFoundError as e:
            return {"error": str(e)}, 404
        except Exception as e:
            return {"error": str(e)}, 500
