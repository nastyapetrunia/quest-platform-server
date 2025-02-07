class EmailInUse(Exception):
    """Exception raised when a user already exists in the system."""

    def __init__(self, message="Provided email is already used."):
        super().__init__(message)

class DatabaseConnectionError(Exception):
    """Raised when there is an issue connecting to the database."""


class DocumentValidationError(Exception):
    """Raised when document validation fails."""


class InsertionError(Exception):
    """Raised when document insertion fails."""