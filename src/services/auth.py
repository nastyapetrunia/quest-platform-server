import datetime
from werkzeug.security import generate_password_hash

from src.database.utils.service import add_new_records
from src.database.utils.collections import Collections
from src.database.user.service import find_user_by_email
from src.utils.exceptions import EmailInUse, InvalidEmail
from src.utils.helpers import generate_jwt_token, validate_email


def signup_with_email(data: dict):
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
        "password": hashed_password,
        "created_at": datetime.datetime.now(datetime.UTC),
        "profile_picture": None,
        "created_quests": [],
        "quest_history": []
    }
    result = add_new_records(collection=Collections.USER, documents=new_user)

    return generate_jwt_token(str(result["inserted_id"]))
