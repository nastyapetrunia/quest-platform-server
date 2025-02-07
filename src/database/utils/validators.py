from typing import Type, Union, List, Dict, Any
from pydantic import BaseModel, ValidationError


def validate_records(
    validation_schema: Type[BaseModel], records_to_check: Union[List[Dict[str, Any]], Dict[str, Any]]
) -> Dict[str, Any]:
    """
    Validates a list of records or a single record against a specified Pydantic schema.

    Args:
        validation_schema (Type[BaseModel]): The Pydantic schema class used for validation.
        records_to_check (Union[List[Dict[str, Any]], Dict[str, Any]]): A list of records or a single record.

    Returns:
        Dict[str, Any]: A dictionary containing:
            - "success" (bool): `True` if all records are valid, `False` if any fail validation.
            - "failed_records" (List[Dict[str, Any]]): List of failed records with error details.
    """
    failed_records = []
    success = True

    records = records_to_check if isinstance(records_to_check, list) else [records_to_check]

    for record in records:
        try:
            validation_schema(**record)
        except ValidationError as e:
            failed_records.append({"record": record, "error": str(e)})
            success = False

    return {"success": success, "failed_records": failed_records}
