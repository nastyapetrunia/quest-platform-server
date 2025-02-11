import os
from bson import ObjectId
from bson.errors import InvalidId

from src.utils.helpers import upload_to_s3
from src.database.quest.schema import QuestRating
from src.database.utils.collections import Collections
from src.database.utils.service import read, logger, update_records, custom_update_records

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

