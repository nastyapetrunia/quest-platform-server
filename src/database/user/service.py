import os
from bson import ObjectId
from bson.errors import InvalidId

from src.utils.helpers import upload_to_s3
from src.database.utils.collections import Collections
from src.database.utils.service import read, logger, update_records

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

def update_user_info(user_id: str, data: dict):
    try:
        user_id_obj = ObjectId(user_id)
    except InvalidId as e:
        logger.error("Invalid ObjectId.")
        raise e

    data["_id"] = user_id_obj

    if data.get("profile_picture"):
        profile_picture_url = upload_to_s3(data["profile_picture"])
        data["profile_picture"] = profile_picture_url

    result = update_records(collection=Collections.USER, documents=data)
    return result