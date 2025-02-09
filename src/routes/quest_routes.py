from flask import request
from pydantic import BaseModel, ValidationError
from flask_restx import Namespace, Resource, fields

from src.utils.exceptions import *
from src.services.quest import create_quest
from src.utils.helpers import format_payload_validation_errors, token_required

quest_ns = Namespace("quest", description="Quest Operations.")

@quest_ns.route("")
class CreateQuest(Resource):
    @quest_ns.response(201, 'Quest successfully created')
    @quest_ns.response(400, 'Bad Request')
    @quest_ns.response(500, 'Internal Server Error')
    def post(self):
        data = request.form.to_dict()

        files = {}
        for level_id in request.files:
            files[level_id] = request.files.getlist(level_id)

        try:
            result = create_quest(data=data, files=files)
            print(result)
            return result, 201
        except (EmailInUse, ValueError, DocumentValidationError, InvalidEmail) as e:
            return {"error": str(e)}, 400
        except (DatabaseConnectionError, InsertionError, Exception) as e:
            return {"error": str(e)}, 500
