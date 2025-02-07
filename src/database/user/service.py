import os
from src.database.utils.service import read

MONGO_DB_NAME = os.getenv("MONGO_DB_NAME")

def find_user_by_email(user_email, ) -> dict:
    return read(db_name=MONGO_DB_NAME,
                collection_name="Users",
                query={"email": user_email},
                find_one=True,
                exclude_id=False)
