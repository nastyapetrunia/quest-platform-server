from typing import Optional

from bson.errors import InvalidId

from flask import request
from pydantic import BaseModel, ValidationError
from flask_restx import Namespace, Resource, fields

from src.utils.exceptions import *
from src.services.user import get_user_by_id, update_user, get_user_quest_history, update_user_quest_history
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

quest_history_model = user_ns.model("QuestHistory", {
    "quest_id": fields.String(required=True, description="Unique identifier for the quest"),
    "quest_difficulty": fields.String(required=True, description="Quest difficulty"),
    "quest_name":  fields.String(required=True, description="Quest name"),
    "quest_main_picture": fields.String(required=True, description="Quest main picture url"),
    "result": fields.Integer(required=False, description="Score the user achieved, or None if not finished"),
    "completed": fields.Boolean(required=True, description="Indicates if the quest was completed"),
    "time_spent": fields.Integer(required=False, description="Time spent on the quest (in seconds)"),
    "rating": fields.Float(required=False, description="Rating the user gave to the quest (if any)"),
    "attempted_at": fields.DateTime(description="Timestamp of when the quest was attempted"),
})

user_quest_history_model = user_ns.model("UserQuestHistory", {
    "quest_history": fields.List(fields.Nested(quest_history_model), description="List of quests attempted by the user"),
})

# Payload model for updating user info
update_user_model = user_ns.model("UpdateUser", {
    "name": fields.String(description="New user name", required=False),
    "profile_picture": fields.Raw(description="New profile picture file", required=False),
})

update_quest_history_model = user_ns.model("UpdateQuestHistoryPayload", {
    "quest_id": fields.String(required=True, description="Unique identifier for the quest"),
    "result": fields.Integer(required=False, description="Score the user achieved, or None if not finished"),
    "completed": fields.Boolean(required=True, description="Indicates if the quest was completed"),
    "time_spent": fields.Integer(required=False, description="Time spent on the quest (in seconds)"),
})


class UpdateQuestHistoryPayload(BaseModel):
    quest_id: str
    result: Optional[int] = None
    completed: bool = False
    time_spent: Optional[int] = None

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

@user_ns.route("/<string:user_id>/quest_history")
@user_ns.param("user_id", "The unique ID of the user")
class UserQuestHistoryResource(Resource):
    @user_ns.response(200, "Success", user_quest_history_model)
    @user_ns.response(404, "User not found")
    @user_ns.response(401, "Unauthorized")
    @token_required
    def get(self, user_id):
        """Retrieve user quest history by user ID"""
        try:
            quest_history = get_user_quest_history(user_id)

            for quest in quest_history:
                quest["quest_id"] = str(quest["quest_id"])
                quest["attempted_at"] = quest["attempted_at"].isoformat()

            return {"quest_history": quest_history}, 200
        except (ValueError, InvalidId) as e:
            return {"error": str(e)}, 400
        except NotFoundError as e:
            return {"error": str(e)}, 404
        except Exception as e:
            return {"error": str(e)}, 500

    @user_ns.expect(update_quest_history_model)
    @user_ns.response(200, "Success")
    @user_ns.response(404, "User not found")
    @user_ns.response(401, "Unauthorized")
    @token_required
    def patch(self, user_id):
        """Add new user quest history record"""
        if user_id != request.user_id:
            return {"error": "Unauthorized access"}, 401

        data = request.get_json()

        try:
            UpdateQuestHistoryPayload(**data)
        except ValidationError as e:
            return {"error": format_payload_validation_errors(e.errors())}, 400

        try:
            quest_history = update_user_quest_history(user_id=user_id,
                                                      new_quest_history=data)
            return quest_history, 200
        except (ValueError, InvalidId) as e:
            return {"error": str(e)}, 400
        except NotFoundError as e:
            return {"error": str(e)}, 404
        except Exception as e:
            return {"error": str(e)}, 500
