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

class InvalidEmail(Exception):
    """Raised when email validation fails."""

class WrongEmailOrPassword(Exception):
    """Raised when user is trying to log in with invalid credentials"""
    def __init__(self, message="Wrong email or password"):
        super().__init__(message)

class NotFoundError(Exception):
    """Raised when document is not found in DB."""
    def __init__(self, message="Document is not found in DB"):
        super().__init__(message)

class UpdateError(Exception):
    """Raised when an error occurred when trying to update document(s) in DB."""

class Unauthorized(Exception):
    """Raised when user attempts to request resource they are not allowed to request."""
