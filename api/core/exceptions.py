"""Custom exceptions for Uni Pilot API."""


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

