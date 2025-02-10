import json

from flask import request
from pydantic import BaseModel, ValidationError
from flask_restx import Namespace, Resource, fields

from src.utils.exceptions import *
from src.services.quest import create_quest
from src.utils.helpers import format_payload_validation_errors, token_required

quest_ns = Namespace("quest", description="Quest Operations.")
quis_option_model = quest_ns.model("Option", {
    "text": fields.String(required=True, description="The text of the quiz option"),
    "id": fields.String(required=True, description="Unique identifier for the quiz option")
})

quis_level_model = quest_ns.model('Level', {
    "type": fields.String(required=True, description="Type of the level, e.g., 'quiz' or 'input'"),
    "id": fields.String(required=True, description="Unique identifier for the level"),
    "name": fields.String(required=True, description="Name of the level"),
    "question": fields.String(required=True, description="The question for the level"),
    "picture_urls": fields.List(fields.String, description="URLs of pictures for the level"),
    "options": fields.List(fields.Nested(quis_option_model), required=False, description="List of options for the quiz question"),
    "try_limit": fields.Integer(required=False, description="The number of attempts allowed for the input level"),
    "correct_option_id": fields.String(required=False, description="The ID of the correct quiz option")
})

create_quest_model = quest_ns.model('CreateQuest', {
    "name": fields.String(required=True, description='Name of the quest'),
    "title": fields.String(required=True, description="Title of the level"),
    "description": fields.String(required=True, description='Description of the quest'),
    "time_limit": fields.Integer(required=True, description='Time limit for completing the quest (in seconds)'),
    "difficulty": fields.String(required=True, description='Difficulty level of the quest'),
    "main_picture": fields.String(required=False, description='URL of the main picture for the quest (optional)'),
    "levels": fields.List(fields.Nested(quis_level_model), description="A list of levels in the quest (can be input or quiz levels)"),
})

@quest_ns.route("")
class CreateQuest(Resource):
    @quest_ns.expect(create_quest_model)
    @quest_ns.response(201, 'Quest successfully created')
    @quest_ns.response(400, 'Bad Request')
    @quest_ns.response(500, 'Internal Server Error')
    @token_required
    def post(self):
        data = request.form.to_dict()
        data["levels"] = json.loads(data.get("levels", "[]"))
        data["created_by"] = request.user_id

        files = {}
        for level_id in request.files:
            files[level_id] = request.files.getlist(level_id)

        try:
            result = create_quest(data=data, files=files)
            return result, 201
        except (EmailInUse, ValueError, DocumentValidationError, InvalidEmail) as e:
            return {"error": str(e)}, 400
        except (DatabaseConnectionError, InsertionError, Exception) as e:
            return {"error": str(e)}, 500

@quest_ns.route("/<string:quest_id>")
@quest_ns.param("quest_id", "The unique ID of the quest")
class GetUpdateQuest(Resource):
    @quest_ns.expect(create_quest_model)
    @quest_ns.response(201, 'Quest successfully created')
    @quest_ns.response(400, 'Bad Request')
    @quest_ns.response(500, 'Internal Server Error')
    @token_required
    def get(self):
        data = request.form.to_dict()
        data["levels"] = json.loads(data.get("levels", "[]"))
        data["created_by"] = request.user_id

        files = {}
        for level_id in request.files:
            files[level_id] = request.files.getlist(level_id)

        try:
            result = create_quest(data=data, files=files)
            return result, 201
        except (EmailInUse, ValueError, DocumentValidationError, InvalidEmail) as e:
            return {"error": str(e)}, 400
        except (DatabaseConnectionError, InsertionError, Exception) as e:
            return {"error": str(e)}, 500