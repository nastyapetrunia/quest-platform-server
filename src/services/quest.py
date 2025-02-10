import datetime
from bson import ObjectId
from bson.errors import InvalidId

from src.services.user import update_user
from src.services.general import upload_files
from src.utils.exceptions import NotFoundError
from src.database.utils.collections import Collections
from src.database.utils.service import add_new_records
from src.database.quest.service import find_quest_by_id, find_all_quests


def create_quest(data: dict, files: dict) -> dict:

    uploaded_pictures = {}
    for key, files in files.items():
        uploaded_pictures[key] = list(upload_files(files).values())

    if uploaded_pictures.get("main_picture"):
        data["main_picture"] = uploaded_pictures.get("main_picture")[0]
    else:
        data["main_picture"] = None

    for level in data["levels"]:
        level["picture_urls"] = uploaded_pictures.get(level["id"], [])

    data["created_at"] = datetime.datetime.now(datetime.UTC)
    data["time_limit"] = int(data["time_limit"])

    try:
        data["created_by"] = ObjectId(data["created_by"])
    except InvalidId as e:
        raise e

    result = add_new_records(collection=Collections.QUEST, documents=data)

    update_user_with_quest = {"created_quests": data["_id"]}
    update_user(user_id=data["created_by"], data=update_user_with_quest, update_type="$addToSet", safe_mode=False)

    data["_id"] = str(result["inserted_id"])
    data["created_by"] = str(data["created_by"])
    data["created_at"] = data["created_at"].isoformat()

    return data

def get_quest_by_id(quest_id: str):
    result = find_quest_by_id(quest_id)
    quest = result["result"]

    if not quest:
        raise NotFoundError()

    quest["_id"] = str(quest["_id"])
    quest["created_by"] = str(quest["created_by"])
    quest["created_at"] = quest["created_at"].isoformat()

    return quest

def get_all_quests():
    result = find_all_quests()
    all_quests = result["result"]

    for doc in all_quests:
        doc["_id"] = str(doc["_id"])
        doc["created_by"] = str(doc["created_by"])
        doc["created_at"] = doc["created_at"].isoformat()

    return all_quests
