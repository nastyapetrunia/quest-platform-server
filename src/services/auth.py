import datetime
from typing import Tuple
from werkzeug.security import generate_password_hash, check_password_hash

from src.database.utils.service import add_new_records
from src.database.utils.collections import Collections
from src.database.user.service import find_user_by_email
from src.utils.helpers import generate_jwt_token, validate_email
from src.utils.exceptions import EmailInUse, InvalidEmail, WrongEmailOrPassword


def signup_with_email(data: dict) -> Tuple[str, dict]:
    """
    Registers a new user by signing up with an email, name, and password.

    This function checks if the email is already in use. If the email is not in use,
    it hashes the user's password and creates a new user record in the database. It then
    generates and returns a JSON Web Token (JWT) for the newly created user.

    Args:
        data (dict): A dictionary containing user details with the following keys:
            - "email" (str): The user's email address.
            - "password" (str): The user's password.
            - "name" (str): The user's name.

    Raises:
        EmailInUse: If the provided email is already associated with an existing user.

    Returns:
        str: A JWT token for the newly created user.
        dict: Created user info
    """
    user_email = data["email"]
    user_password = data["password"]
    user_name = data["name"]

    email_validation_success, message = validate_email(user_email=user_email)
    if not email_validation_success:
        raise InvalidEmail(message)

    existing_user = find_user_by_email(user_email)

    if existing_user["result"]:
        raise EmailInUse()

    hashed_password = generate_password_hash(user_password)

    new_user = {
        "name": user_name,
        "email": user_email,
        "about_me": "",
        "password": hashed_password,
        "created_at": datetime.datetime.now(datetime.UTC),
        "profile_picture": None,
        "created_quests": [],
        "quest_history": []
    }
    result = add_new_records(collection=Collections.USER, documents=new_user)

    new_user["_id"] = str(result["inserted_id"])
    new_user["created_at"] = new_user["created_at"].isoformat()
    del new_user["password"]

    return generate_jwt_token(new_user["_id"]), new_user

def login_with_email(data: dict) -> Tuple[str, dict]:
    """
    Authenticates a user by email and password.

    This function checks if a user with the provided email exists in the database.
    If the user exists, it verifies the password against the stored hashed password.
    Upon successful authentication, a JSON Web Token (JWT) is generated and returned.

    Args:
        data (dict): A dictionary containing the user's login credentials:
            - "email" (str): The user's email address.
            - "password" (str): The user's password.

    Raises:
        WrongEmailOrPassword: If the email does not exist or the password is incorrect.

    Returns:
        str: A JWT token for the authenticated user.
        dict: User info
    """
    user_email = data["email"]
    user_password = data["password"]

    result = find_user_by_email(user_email)
    existing_user = result["result"]

    if not existing_user:
        raise WrongEmailOrPassword()

    if not check_password_hash(existing_user["password"], user_password):
        raise WrongEmailOrPassword()

    token = generate_jwt_token(str(existing_user["_id"]))

    existing_user["_id"] = str(existing_user["_id"])
    existing_user["created_at"] = existing_user["created_at"].isoformat()
    existing_user["created_quests"] = [str(quest) for quest in existing_user["created_quests"]]

    for quest in existing_user["quest_history"]:
        quest["quest_id"] = str(quest["quest_id"])
        quest["attempted_at"] = quest["attempted_at"].isoformat()

    del existing_user["password"]

    return token, existing_user
