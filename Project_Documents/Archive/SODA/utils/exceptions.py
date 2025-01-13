"""SODA exception classes module."""

class SodaError(Exception):
    """Base exception for SODA-related errors."""
    
    def __init__(self, message: str, status_code: int = None):
        """Initialize SODA error."""
        super().__init__(message)
        self.status_code = status_code

class AuthenticationError(SodaError):
    """Exception for authentication errors."""
    pass

class ResourceNotFoundError(SodaError):
    """Exception for resource not found errors."""
    pass

class ValidationError(SodaError):
    """Exception for validation errors."""
    pass

class RateLimitError(SodaError):
    """Exception for rate limit errors."""
    pass

class ServerError(SodaError):
    """Exception for server errors."""
    pass
