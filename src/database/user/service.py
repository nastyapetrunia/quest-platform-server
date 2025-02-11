import os
import datetime
from typing import Union
from bson import ObjectId
from bson.errors import InvalidId

from src.utils.helpers import upload_to_s3
from src.database.utils.collections import Collections
from src.database.utils.service import read, logger, update_records, aggregate

MONGO_DB_NAME = os.getenv("MONGO_DB_NAME")

def find_user_by_email(user_email: str) -> dict:
    return read(db_name=MONGO_DB_NAME,
                collection_name="Users",
                query={"email": user_email},
                find_one=True,
                exclude_id=False)

def find_user_by_id(user_id: str) -> dict:
    try:
        user_id_obj = ObjectId(user_id)
    except InvalidId as e:
        logger.error("Invalid ObjectId.")
        raise e

    return read(db_name=MONGO_DB_NAME,
                collection_name="Users",
                query={"_id": user_id_obj},
                find_one=True,
                exclude_id=False)

def update_user_info(user_id: Union[str, ObjectId],
                     data: dict,
                     update_type: str = "$set",
                     safe_mode: bool = True,
                     custom_validate_rule = None):
    if isinstance(user_id, str):
        try:
            user_id_obj = ObjectId(user_id)
            data["_id"] = user_id_obj
        except InvalidId as e:
            logger.error("Invalid ObjectId.")
            raise e
    else:
        data["_id"] = user_id

    result = {}

    if data.get("profile_picture"):
        profile_picture_url = upload_to_s3(data["profile_picture"])
        data["profile_picture"] = profile_picture_url
        result["profile_picture_url"] = profile_picture_url

    update_result = update_records(collection=Collections.USER,
                                   documents=data,
                                   update_type=update_type,
                                   safe_mode=safe_mode,
                                   custom_validate_rule=custom_validate_rule)
    result["message"] = update_result["message"]

    return result

def get_user_quest_history_full_info(user_id: Union[str, ObjectId]):
    if isinstance(user_id, str):
        try:
            user_id_obj = ObjectId(user_id)
        except InvalidId as e:
            logger.error("Invalid ObjectId.")
            raise e
    else:
        user_id_obj = user_id

    pipeline = [
        {"$match": {"_id": user_id_obj}},
        {"$unwind": "$quest_history"},
        {"$lookup": {
            "from": "Quests",
            "localField": "quest_history.quest_id",
            "foreignField": "_id",
            "as": "quest_details"
        }},
        {"$unwind": "$quest_details"},
        {"$project": {
            "_id": 0,
            "quest_id": "$quest_history.quest_id",
            "quest_name": "$quest_details.name",
            "quest_difficulty": "$quest_details.difficulty",
            "quest_main_picture": "$quest_details.main_picture",
            "result": "$quest_history.result",
            "completed": "$quest_history.completed",
            "time_spent": "$quest_history.time_spent",
            "attempted_at": "$quest_history.attempted_at",
            "user_rating": "$quest_history.rating"
        }}
    ]

    return aggregate(collection=Collections.USER,
                     pipeline=pipeline)

def add_new_user_quest_history(user_id: Union[str, ObjectId],
                              data: dict):
    new_data = {}
    if isinstance(user_id, str):
        try:
            user_id_obj = ObjectId(user_id)
            new_data["_id"] = user_id_obj

        except InvalidId as e:
            logger.error("Invalid ObjectId.")
            raise e
    else:
        new_data["_id"] = user_id

    data["quest_id"] = ObjectId(data["quest_id"])
    data["attempted_at"] = datetime.datetime.now(datetime.UTC)

    new_data["quest_history"] = data

    update_result = update_records(collection=Collections.USER,
                                   documents=new_data,
                                   update_type="$push",
                                   safe_mode=False)

    return update_result