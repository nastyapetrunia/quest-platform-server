import os
from bson import ObjectId
from bson.errors import InvalidId

from src.utils.helpers import upload_to_s3
from src.database.quest.schema import QuestRating
from src.database.utils.collections import Collections
from src.database.utils.service import read, logger, update_records, custom_update_records, aggregate

MONGO_DB_NAME = os.getenv("MONGO_DB_NAME")

def find_quest_by_id(quest_id: str) -> dict:
    try:
        quest_id_obj = ObjectId(quest_id)
    except InvalidId as e:
        logger.error("Invalid ObjectId.")
        raise e

    return read(db_name=MONGO_DB_NAME,
                collection_name="Quests",
                query={"_id": quest_id_obj},
                find_one=True,
                exclude_id=False)

def find_all_quests():

    return read(db_name=MONGO_DB_NAME,
                collection_name="Quests",
                query={},
                find_one=False,
                exclude_id=False)

def add_new_rating(_id: ObjectId, rating: dict, avg_rating: float):
    custom_query = {
        "$push": {"ratings": rating},
        "$set": {"avg_rating": avg_rating}
    }
    return custom_update_records(collection=Collections.QUEST,
                                 _id=_id,
                                 custom_query=custom_query,
                                 validate_with=QuestRating,
                                 validate_dict=rating)

def get_quest_ratings_full_info(quest_id: str):
    if isinstance(quest_id, str):
        try:
            quest_id_obj = ObjectId(quest_id)
        except InvalidId as e:
            logger.error("Invalid ObjectId.")
            raise e
    else:
        quest_id_obj = quest_id

    pipeline = [
        {"$match": {"_id": quest_id_obj}},
        {"$unwind": "$ratings"},
        {"$lookup": {
            "from": "Users",
            "localField": "ratings.user_id",
            "foreignField": "_id",
            "as": "user_details"
        }},
        {"$unwind": "$user_details"},
        {"$project": {
            "_id": 0,
            "rating": "$ratings.rating",
            "review": "$ratings.review",
            "user_id": "$ratings.user_id",
            "user_name": "$user_details.name",
            "user_profile_picture": "$user_details.profile_picture"
        }}
    ]

    return aggregate(collection=Collections.QUEST,
                     pipeline=pipeline)