import os
import logging

from dotenv import load_dotenv
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi

logger = logging.getLogger('myLog')
load_dotenv()

MONGO_URI = os.getenv("MONGO_URI")
client = MongoClient(MONGO_URI, server_api=ServerApi('1'))

def test_connection() -> dict:
    """
    Tests the connection to the MongoDB server by sending a ping command.

    Returns:
        dict: A dictionary containing the connection status.
              - If successful: {"success": True, "message": "Pinged deployment. Successfully connected to MongoDB!"}
              - If failed: {"success": False, "message": "Error message: <error details>"}
    """
    try:
        client.admin.command('ping')
        logger.info("Successfully connected to MongoDB.")
        return {"success": True, "message": "Pinged deployment. Successfully connected to MongoDB!"}
    except Exception as e:
        logger.error(f"Error message: {e}")
        return {"success": False, "message": f"Error message: {e}"}

test_connection()
