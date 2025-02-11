from src.utils.exceptions import NotFoundError
from src.database.user.service import find_user_by_id, update_user_info, get_user_quest_history_full_info, add_new_user_quest_history

def get_user_by_id(user_id: str):
    result = find_user_by_id(user_id)
    user = result["result"]

    if not user:
        raise NotFoundError()

    user["_id"] = str(user["_id"])
    user["created_at"] = user["created_at"].isoformat()
    del user["password"]

    return user

def update_user(user_id: str, data: dict, update_type: str = "$set", safe_mode: bool = True):
    result = update_user_info(user_id=user_id,
                              data=data,
                              update_type=update_type,
                              safe_mode=safe_mode)

    return result

def get_user_quest_history(user_id: str):

    quest_history = get_user_quest_history_full_info(user_id=user_id)

    return quest_history

def update_user_quest_history(user_id: str,
                              new_quest_history: dict):

    result = add_new_user_quest_history(user_id=user_id,
                                        data=new_quest_history)

    return result