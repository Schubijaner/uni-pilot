"""Custom exceptions for Uni Pilot API."""

from fastapi import HTTPException, status


class UniPilotException(Exception):
    """Base exception for all Uni Pilot exceptions."""

    def __init__(self, message: str, error_code: str = None):
        self.message = message
        self.error_code = error_code or self.__class__.__name__
        super().__init__(self.message)


class NotFoundError(UniPilotException):
    """Resource not found."""

    pass


class ValidationError(UniPilotException):
    """Validation error."""

    pass


class AuthenticationError(UniPilotException):
    """Authentication failed."""

    pass


class AuthorizationError(UniPilotException):
    """Authorization failed (insufficient permissions)."""

    pass


class LLMError(UniPilotException):
    """LLM API error."""

    pass


class CredentialException(HTTPException):
    """Custom exception for authentication/authorization errors."""

    def __init__(self):
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

