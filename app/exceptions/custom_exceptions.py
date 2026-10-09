
class ValidationError(Exception):
    """Raised when input validation fails."""
    pass


class ResourceNotFoundError(Exception):
    """Raised when a requested resource does not exist."""
    pass


class ResourceConflictError(Exception):
    """Raised when a resource conflicts with existing data."""
    pass