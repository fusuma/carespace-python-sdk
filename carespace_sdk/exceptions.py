"""
Exception classes for the Carespace SDK.
"""

from typing import Any, Dict, Optional


class CarespaceError(Exception):
    """Base exception for all Carespace SDK errors."""

    def __init__(
        self,
        message: str,
        status_code: Optional[int] = None,
        response_data: Optional[Dict[str, Any]] = None,
    ) -> None:
        super().__init__(message)
        self.message = message
        self.status_code = status_code
        self.response_data = response_data or {}

    def __str__(self) -> str:
        if self.status_code:
            return f"HTTP {self.status_code}: {self.message}"
        return self.message

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(message={self.message!r}, status_code={self.status_code})"


class AuthenticationError(CarespaceError):
    """Raised when authentication fails."""

    def __init__(
        self,
        message: str = "Authentication failed. Please check your API key.",
        status_code: Optional[int] = 401,
        response_data: Optional[Dict[str, Any]] = None,
    ) -> None:
        super().__init__(message, status_code, response_data)


class ValidationError(CarespaceError):
    """Raised when request validation fails."""

    def __init__(
        self,
        message: str,
        status_code: Optional[int] = 400,
        response_data: Optional[Dict[str, Any]] = None,
    ) -> None:
        super().__init__(message, status_code, response_data)


class NotFoundError(CarespaceError):
    """Raised when a resource is not found."""

    def __init__(
        self,
        message: str = "Resource not found",
        status_code: Optional[int] = 404,
        response_data: Optional[Dict[str, Any]] = None,
    ) -> None:
        super().__init__(message, status_code, response_data)


class ServerError(CarespaceError):
    """Raised when the server encounters an error."""

    def __init__(
        self,
        message: str = "Internal server error",
        status_code: Optional[int] = 500,
        response_data: Optional[Dict[str, Any]] = None,
    ) -> None:
        super().__init__(message, status_code, response_data)


class NetworkError(CarespaceError):
    """Raised when a network error occurs."""

    def __init__(
        self,
        message: str = "Network error occurred",
        original_exception: Optional[Exception] = None,
    ) -> None:
        super().__init__(message)
        self.original_exception = original_exception

    def __str__(self) -> str:
        if self.original_exception:
            return f"{self.message}: {self.original_exception}"
        return self.message


class RateLimitError(CarespaceError):
    """Raised when rate limit is exceeded."""

    def __init__(
        self,
        message: str = "Rate limit exceeded",
        status_code: Optional[int] = 429,
        retry_after: Optional[int] = None,
        response_data: Optional[Dict[str, Any]] = None,
    ) -> None:
        super().__init__(message, status_code, response_data)
        self.retry_after = retry_after


class TimeoutError(CarespaceError):
    """Raised when a request times out."""

    def __init__(
        self,
        message: str = "Request timed out",
        timeout_duration: Optional[float] = None,
    ) -> None:
        super().__init__(message)
        self.timeout_duration = timeout_duration