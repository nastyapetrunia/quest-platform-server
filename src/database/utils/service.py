import os
import logging
from bson import ObjectId
from pydantic import BaseModel
from dotenv import load_dotenv
from typing import List, Union, Type
from pymongo import errors, UpdateOne

from src.database.utils.setup import client
from src.database.utils.collections import Collections
from src.database.utils.validators import validate_records
from src.utils.exceptions import InsertionError, DatabaseConnectionError, DocumentValidationError, UpdateError, NotFoundError

load_dotenv()
logger = logging.getLogger('myLog')

DB_NAME = os.getenv("MONGO_DB_NAME")

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
        result = validate_records(collection.value.validation_schema_create, documents)
        if not result["success"]:
            logger.error(f"Failed document validation for {collection_name} Collection. Info: {result["failed_records"]}. "
                        f"To force add new records, set safe_mode=False (not recommended).")
            raise DocumentValidationError("Failed validation.")
    else:
        logger.info("Safe mode is off.")
        logger.warning("Force adding new records without validation is not recommended.")

    db_name = DB_NAME
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

def _update(documents: Union[List[dict], dict],
            db_name: str,
            collection_name: str,
            update_type: str = "$set") -> dict:
    """
    Updates one or more documents in a specified MongoDB collection.

    Args:
        documents: A single document (dict) or a list of documents (list of dicts) to be updated.
        db_name: Name of the database where the collection is located.
        collection_name: Name of the collection to update documents in.

    Raises:
        ValueError: If `documents` is empty or if `db_name` or `collection_name` is empty.
        DatabaseConnectionError: If there are issues connecting to the database.
        UpdateError: If update fails due to issues with the documents or MongoDB operations.
    """
    if not documents:
        raise ValueError("No documents to update.")
    if not db_name or not collection_name:
        raise ValueError("db_name and collection_name cannot be empty.")

    try:
        db = client[db_name]
        collection = db[collection_name]

        if isinstance(documents, list):
            success_return_message = "Successfully updated documents."
            result = collection.bulk_write([
                UpdateOne({'_id': doc['_id']}, {update_type: doc}) for doc in documents
            ], ordered=False)
            logger.info(f"Updated document IDs: {result.modified_count}")
        else:
            success_return_message = "Successfully updated document."
            document_id = documents.pop('_id')
            result = collection.update_one({'_id': document_id}, {update_type: documents})
            logger.info(f"Updated document ID: {document_id}")

        if result.matched_count == 0:
            raise NotFoundError("No matching documents found to update.")

        if result.modified_count == 0:
            return {"success": True, "message": "No changes were made."}
        else:
            return {"success": True, "message": success_return_message}

    except errors.BulkWriteError as e:
        logger.error(f"Bulk write error occurred: {e.details}")
        raise UpdateError(f"Failed bulk update. Info: {e.details}")
    except Exception as e:
        logger.error(f"Failed to update records in {collection_name}.")
        logger.error(f"Error occurred during update: {str(e)}")
        raise UpdateError(f"Failed to update documents. Info: {str(e)}")

def _custom_query_update(db_name: str,
                         collection_name: str,
                         _id: ObjectId,
                         custom_query: dict) -> dict:
    """
    Updates one or more documents in a specified MongoDB collection.

    Args:
        documents: A single document (dict) or a list of documents (list of dicts) to be updated.
        db_name: Name of the database where the collection is located.
        collection_name: Name of the collection to update documents in.

    Raises:
        ValueError: If `documents` is empty or if `db_name` or `collection_name` is empty.
        DatabaseConnectionError: If there are issues connecting to the database.
        UpdateError: If update fails due to issues with the documents or MongoDB operations.
    """
    if not custom_query or not _id:
        raise ValueError("Nothing to update.")
    if not db_name or not collection_name:
        raise ValueError("db_name and collection_name cannot be empty.")

    try:
        db = client[db_name]
        collection = db[collection_name]

        update_query = [
            UpdateOne(
                {"_id": _id},  # Quest filter
                custom_query
            )
        ]

        result = collection.bulk_write(update_query)

        if result.matched_count == 0:
            raise NotFoundError("No matching documents found to update.")

        if result.modified_count == 0:
            return {"success": True, "message": "No changes were made."}
        else:
            return {"success": True, "message": "Successfully updated document."}

    except errors.BulkWriteError as e:
        logger.error(f"Bulk write error occurred: {e.details}")
        raise UpdateError(f"Failed bulk update. {e.details}")
    except Exception as e:
        logger.error(f"Failed to update records in {collection_name}.")
        logger.error(f"Error occurred during update: {str(e)}")
        raise UpdateError(f"Failed to update documents. Info: {str(e)}")

def update_records(collection: Collections,
                   documents: Union[List[dict], dict],
                   safe_mode: bool = True,
                   update_type: str = "$set"):
    """
    Updates existing records in a specified MongoDB collection with optional safety validation.

    Raises:
        DocumentValidationError: If validation fails in safe mode.
        DatabaseConnectionError: If `db_name` is missing.
        UpdateError: If update operation fails.
    """
    collection_name = collection.value.name

    if safe_mode:
        result = validate_records(collection.value.validation_schema_update, documents)
        if not result["success"]:
            logger.error(f"Failed document validation for {collection_name} Collection. Info: {result['failed_records']}. "
                        f"To force update records, set safe_mode=False (not recommended).")
            raise DocumentValidationError("Failed validation.")
    else:
        logger.info("Safe mode is off.")
        logger.warning("Force updating records without validation is not recommended.")

    db_name = DB_NAME
    if not db_name:
        raise DatabaseConnectionError("Database name is not set in environment variables.")

    return _update(documents, db_name, collection_name, update_type=update_type)

def custom_update_records(collection: Collections,
                          _id: ObjectId,
                          custom_query: dict,
                          validate_with: Type[BaseModel] = None,
                          validate_dict: dict = None,
                          safe_mode: bool = True):

    collection_name = collection.value.name

    if safe_mode:
        result = validate_records(validate_with, validate_dict)
        if not result["success"]:
            logger.error(f"Failed document validation for {collection_name} Collection. Info: {result['failed_records']}. "
                        f"To force update records, set safe_mode=False (not recommended).")
            raise DocumentValidationError("Failed validation.")
    else:
        logger.info("Safe mode is off.")
        logger.warning("Force updating records without validation is not recommended.")

    db_name = DB_NAME
    if not db_name:
        raise DatabaseConnectionError("Database name is not set in environment variables.")

    return _custom_query_update(db_name=db_name,
                                collection_name=collection_name,
                                _id=_id,
                                custom_query=custom_query)
