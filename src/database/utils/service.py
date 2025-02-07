import os
import logging
from pymongo import errors
from typing import List, Union
from dotenv import load_dotenv

from src.database.utils.setup import client
from src.database.utils.collections import Collections
from src.database.utils.validators import validate_records
from src.utils.exceptions import InsertionError, DatabaseConnectionError, DocumentValidationError

load_dotenv()
logger = logging.getLogger('myLog')


def _create(documents: Union[List[dict], dict], db_name: str, collection_name: str) -> dict:
    """
    Inserts one or more documents into a specified MongoDB collection.

    Raises:
        DatabaseConnectionError: If `db_name` or `collection_name` is empty.
        InsertionError: If insertion fails.
    """
    if not documents:
        raise ValueError("No documents to insert.")
    if not db_name or not collection_name:
        raise ValueError("db_name and collection_name cannot be empty.")

    try:
        db = client[db_name]
        collection = db[collection_name]

        if isinstance(documents, list):
            result = collection.insert_many(documents, ordered=False)
            logger.info(f"Inserted document IDs: {result.inserted_ids}")
        else:
            result = collection.insert_one(documents)
            logger.info(f"Inserted document ID: {result.inserted_id}")

        return {"success": True, "message": "Successfully inserted documents.", "inserted_id": result.inserted_id}

    except errors.BulkWriteError as e:
        logger.error(f"Bulk write error occurred: {e.details}")
        raise InsertionError(f"Failed bulk write. Info: {e.details}")
    except Exception as e:
        logger.error(f"Error occurred during insertion: {str(e)}")
        raise InsertionError(f"Failed to insert documents. Info: {str(e)}")


def add_new_records(collection: Collections, documents: Union[List[dict], dict], safe_mode: bool = True):
    """
    Adds new records to a specified MongoDB collection with optional safety validation.

    Raises:
        DocumentValidationError: If validation fails in safe mode.
        DatabaseConnectionError: If `db_name` is missing.
        InsertionError: If insertion fails.
    """
    collection_name = collection.value.name

    if safe_mode:
        result = validate_records(collection.value.validation_schema, documents)
        if not result["success"]:
            logger.error(f"Failed document validation for {collection_name} Collection. Info: {result["failed_records"]}. "
                        f"To force add new records, set safe_mode=False (not recommended).")
            raise DocumentValidationError("Failed validation.")
    else:
        logger.info("Safe mode is off.")
        logger.warning("Force adding new records without validation is not recommended.")

    db_name = os.getenv("MONGO_DB_NAME")
    if not db_name:
        raise DatabaseConnectionError("Database name is not set in environment variables.")

    return _create(documents, db_name, collection_name)


def read(db_name: str, collection_name: str, query: dict = None, exclude_id: bool = True, find_one: bool = False):
    """
    Retrieves records from a specified MongoDB collection.

    Raises:
        DatabaseConnectionError: If `db_name` or `collection_name` is missing.
        ReadError: If reading from the database fails.
    """
    if not db_name or not collection_name:
        raise ValueError("db_name and collection_name cannot be empty.")

    try:
        db = client[db_name]
        collection = db[collection_name]

        if exclude_id:
            exclude_fields_dict = {"_id": 0}
        else:
            exclude_fields_dict = {}

        if find_one:
            document = collection.find_one(query, exclude_fields_dict)
            logger.info(f"Got document: {document}")
            return {"success": True, "result": document}
        else:
            documents = list(collection.find(query, exclude_fields_dict))
            logger.info(f"Got records: {documents}")
            return {"success": True, "result": documents}

    except Exception as e:
        logger.error(f"Failed getting info from DB: {e}")
        raise e
