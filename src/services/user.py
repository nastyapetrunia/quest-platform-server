from src.utils.exceptions import *
from src.database.user.service import find_user_by_id, update_user_info

def get_user_by_id(user_id: str):
    result = find_user_by_id(user_id)
    user = result["result"]

    if not user:
        raise UserNotFoundError()

    user["_id"] = str(user["_id"])
    user["created_at"] = user["created_at"].isoformat()
    del user["password"]

    return user

def update_user(user_id: str, data: dict, update_type: str = "$set", safe_mode: bool = True):
    result = update_user_info(user_id=user_id, data=data, update_type=update_type, safe_mode=safe_mode)

    return result
