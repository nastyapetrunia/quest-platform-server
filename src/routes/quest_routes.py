import json
from bson.errors import InvalidId

from flask import request
from pydantic import BaseModel, ValidationError
from flask_restx import Namespace, Resource, fields

from src.utils.exceptions import *
from src.utils.helpers import format_payload_validation_errors, token_required
from src.services.quest import get_quest_by_id, get_all_quests, rate_quest, create_quest, get_quest_ratings

quest_ns = Namespace("quest", description="Quest Operations.")
quests_ns = Namespace("quests", description="Quests Operations.")

quest_level_option_model = quest_ns.model("Option", {
    "text": fields.String(required=True, description="The text of the quiz option"),
    "id": fields.String(required=True, description="Unique identifier for the quiz option")
})

quest_level_model = quest_ns.model('Level', {
    "type": fields.String(required=True, description="Type of the level, e.g., 'quiz' or 'input'"),
    "id": fields.String(required=True, description="Unique identifier for the level"),
    "name": fields.String(required=True, description="Name of the level"),
    "question": fields.String(required=True, description="The question for the level"),
    "picture_urls": fields.List(fields.String, description="URLs of pictures for the level"),
    "options": fields.List(fields.Nested(quest_level_option_model), required=False, description="List of options for the quiz question"),
    "try_limit": fields.Integer(required=False, description="The number of attempts allowed for the input level"),
    "correct_option_id": fields.String(required=False, description="The ID of the correct quiz option")
})

create_quest_model = quest_ns.model('CreateQuest', {
    "name": fields.String(required=True, description='Name of the quest'),
    "description": fields.String(required=True, description='Description of the quest'),
    "time_limit": fields.Integer(required=True, description='Time limit for completing the quest (in seconds)'),
    "difficulty": fields.String(required=True, description='Difficulty level of the quest'),
    "main_picture": fields.String(required=False, description='URL of the main picture for the quest (optional)'),
    "levels": fields.List(fields.Nested(quest_level_model), description="A list of levels in the quest (can be input or quiz levels)"),
})

quest_response_model = quest_ns.model('Quest', {
    "_id": fields.String(description="Quest's unique identifier (_id) as a string"),
    "name": fields.String(required=True, description='Name of the quest'),
    "description": fields.String(required=True, description='Description of the quest'),
    "time_limit": fields.Integer(required=True, description='Time limit for completing the quest (in seconds)'),
    "difficulty": fields.String(required=True, description='Difficulty level of the quest'),
    "main_picture": fields.String(required=False, description='URL of the main picture for the quest (optional)'),
    "created_by": fields.String(description="Author's unique identifier (_id) as a string"),
    "levels": fields.List(fields.Nested(quest_level_model), description="A list of levels in the quest (can be input or quiz levels)"),
})

quests_response_model = quest_ns.model("QuestsResponse", {
    "quests": fields.List(fields.Nested(quest_response_model), description="A list of all quests")
})

quest_rating_model = quest_ns.model('QuestRating', {
    "rating": fields.Integer(required=True, description='User rating'),
    "review": fields.String(required=False, description='User review')
})

quest_rating_response_model = quest_ns.model('QuestRatingResponse', {
    "rating": fields.Integer(required=True, description='User rating'),
    "review": fields.String(required=False, description='User review'),
    "user_id": fields.String(required=False, description="User's unique identifier (_id) as a string"),
    "user_name": fields.String(required=False, description="User name"),
    "user_profile_picture": fields.String(required=False, description="User profile picture")
})

quest_ratings_response_model = quest_ns.model('QuestRatingsResponse', {
    "quest_ratings": fields.List(fields.Nested(quest_rating_response_model), description="A list of all quest ratings")

})

@quest_ns.route("")
class CreateQuest(Resource):
    @quest_ns.expect(create_quest_model)
    @quest_ns.response(201, 'Quest successfully created', quest_response_model)
    @quest_ns.response(400, 'Bad Request')
    @quest_ns.response(500, 'Internal Server Error')
    @token_required
    def post(self):
        """Create new quest"""
        data = request.form.to_dict()
        data["levels"] = json.loads(data.get("levels", "[]"))
        data["created_by"] = request.user_id

        files = {}
        for level_id in request.files:
            files[level_id] = request.files.getlist(level_id)

        try:
            result = create_quest(data=data, files=files)
            return result, 201
        except (ValueError, DocumentValidationError, InvalidId) as e:
            return {"error": str(e)}, 400
        except (DatabaseConnectionError, InsertionError, Exception) as e:
            return {"error": str(e)}, 500

@quest_ns.route("/<string:quest_id>")
@quest_ns.param("quest_id", "The unique ID of the quest")
class GetUpdateQuest(Resource):
    @quest_ns.response(200, "Success", quest_response_model)
    @quest_ns.response(404, "Quest not found")
    @quest_ns.response(401, "Unauthorized")
    @token_required
    def get(self, quest_id):
        """Retrieve quest information by ID"""
        try:
            quest = get_quest_by_id(quest_id)

            quest["_id"] = str(quest["_id"])
            quest["created_by"] = str(quest["created_by"])
            quest["created_at"] = quest["created_at"].isoformat()

            quest["ratings"] = [{"user_id": str(rating["user_id"]),
                                 "review": rating["review"],
                                 "rating": rating["rating"]} for rating in quest["ratings"]]
            return {"quest": quest}, 200
        except ValueError as e:
            return {"error": str(e)}, 400
        except NotFoundError as e:
            return {"error": str(e)}, 404
        except Exception as e:
            return {"error": str(e)}, 500

    #TODO: update quest

@quest_ns.route("/<string:quest_id>/rate")
@quest_ns.param("quest_id", "The unique ID of the quest")
class RateQuest(Resource):
    @quest_ns.expect(quest_rating_model)
    @quest_ns.response(200, "Success")
    @quest_ns.response(404, "Quest not found")
    @quest_ns.response(401, "Unauthorized")
    @token_required
    def patch(self, quest_id):
        """Rate quest"""
        rating = request.get_json()
        rating["user_id"] = request.user_id

        try:
            result = rate_quest(quest_id=quest_id, rating=rating)

            return result, 200
        except ValueError as e:
            return {"error": str(e)}, 400
        except NotFoundError as e:
            return {"error": str(e)}, 404
        except Exception as e:
            return {"error": str(e)}, 500


@quests_ns.route("")
class AllQuests(Resource):
    @quest_ns.response(200, "Success", quests_response_model)
    @quest_ns.response(400, 'Bad Request')
    @quest_ns.response(500, 'Internal Server Error')
    @token_required
    def get(self):
        """Get all quests"""
        try:
            result = get_all_quests()
            return result, 200
        except Exception as e:
            return {"error": str(e)}, 500

@quest_ns.route("/<string:quest_id>/ratings")
@quest_ns.param("quest_id", "The unique ID of the quest")
class GetQuestRatings(Resource):
    @quest_ns.response(200, "Success", quest_ratings_response_model)
    @quest_ns.response(404, "Quest not found")
    @quest_ns.response(401, "Unauthorized")
    @token_required
    def get(self, quest_id):
        """Retrieve quest ratings with user info by quest ID"""
        try:
            quest_ratings = get_quest_ratings(quest_id)

            for rating in quest_ratings:
                rating["user_id"] = str(rating["user_id"])

            return {"quest_ratings": quest_ratings}, 200
        except ValueError as e:
            return {"error": str(e)}, 400
        except NotFoundError as e:
            return {"error": str(e)}, 404
        except Exception as e:
            return {"error": str(e)}, 500
