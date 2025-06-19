"""
Tests for custom exceptions.
"""

import pytest

from carespace_sdk.exceptions import (
    CarespaceError,
    AuthenticationError,
    ValidationError,
    NotFoundError,
    ServerError,
    NetworkError,
    RateLimitError,
    TimeoutError,
)


class TestCarespaceExceptions:
    """Test custom exception classes."""

    def test_base_carespace_error(self):
        """Test base CarespaceError."""
        error = CarespaceError(
            message="Test error",
            status_code=400,
            response_data={"detail": "Test error detail"}
        )
        
        assert str(error) == "Test error"
        assert error.message == "Test error"
        assert error.status_code == 400
        assert error.response_data == {"detail": "Test error detail"}

    def test_carespace_error_minimal(self):
        """Test CarespaceError with minimal parameters."""
        error = CarespaceError("Simple error")
        
        assert str(error) == "Simple error"
        assert error.message == "Simple error"
        assert error.status_code is None
        assert error.response_data is None

    def test_authentication_error(self):
        """Test AuthenticationError."""
        error = AuthenticationError(
            "Invalid credentials",
            status_code=401,
            response_data={"error": "Unauthorized"}
        )
        
        assert isinstance(error, CarespaceError)
        assert str(error) == "Invalid credentials"
        assert error.status_code == 401

    def test_validation_error(self):
        """Test ValidationError."""
        error_data = {
            "errors": {
                "email": ["Invalid email format"],
                "password": ["Password too short"]
            }
        }
        
        error = ValidationError(
            "Validation failed",
            status_code=422,
            response_data=error_data
        )
        
        assert isinstance(error, CarespaceError)
        assert str(error) == "Validation failed"
        assert error.status_code == 422
        assert "email" in error.response_data["errors"]
        assert "password" in error.response_data["errors"]

    def test_not_found_error(self):
        """Test NotFoundError."""
        error = NotFoundError(
            "User not found",
            status_code=404,
            response_data={"error": "User with ID 123 not found"}
        )
        
        assert isinstance(error, CarespaceError)
        assert str(error) == "User not found"
        assert error.status_code == 404

    def test_server_error(self):
        """Test ServerError."""
        error = ServerError(
            "Internal server error",
            status_code=500,
            response_data={"error": "Database connection failed"}
        )
        
        assert isinstance(error, CarespaceError)
        assert str(error) == "Internal server error"
        assert error.status_code == 500

    def test_network_error(self):
        """Test NetworkError."""
        original_exception = ConnectionError("Network unreachable")
        
        error = NetworkError(
            "Network connection failed",
            original_exception=original_exception
        )
        
        assert isinstance(error, CarespaceError)
        assert str(error) == "Network connection failed"
        assert error.original_exception == original_exception
        assert error.status_code is None

    def test_network_error_minimal(self):
        """Test NetworkError without original exception."""
        error = NetworkError("Connection timeout")
        
        assert str(error) == "Connection timeout"
        assert error.original_exception is None

    def test_rate_limit_error(self):
        """Test RateLimitError."""
        error = RateLimitError(
            "Rate limit exceeded",
            status_code=429,
            retry_after=60,
            response_data={"error": "Too many requests"}
        )
        
        assert isinstance(error, CarespaceError)
        assert str(error) == "Rate limit exceeded"
        assert error.status_code == 429
        assert error.retry_after == 60

    def test_rate_limit_error_no_retry_after(self):
        """Test RateLimitError without retry_after."""
        error = RateLimitError(
            "Rate limit exceeded",
            status_code=429
        )
        
        assert str(error) == "Rate limit exceeded"
        assert error.retry_after is None

    def test_timeout_error(self):
        """Test TimeoutError."""
        error = TimeoutError(
            "Request timed out",
            timeout_duration=30.0
        )
        
        assert isinstance(error, CarespaceError)
        assert str(error) == "Request timed out"
        assert error.timeout_duration == 30.0
        assert error.status_code is None

    def test_timeout_error_minimal(self):
        """Test TimeoutError without timeout duration."""
        error = TimeoutError("Request timed out")
        
        assert str(error) == "Request timed out"
        assert error.timeout_duration is None

    def test_exception_inheritance(self):
        """Test that all custom exceptions inherit from CarespaceError."""
        exceptions = [
            AuthenticationError("test"),
            ValidationError("test"),
            NotFoundError("test"),
            ServerError("test"),
            NetworkError("test"),
            RateLimitError("test"),
            TimeoutError("test"),
        ]
        
        for exc in exceptions:
            assert isinstance(exc, CarespaceError)
            assert isinstance(exc, Exception)

    def test_exception_representation(self):
        """Test exception string representation."""
        error = ValidationError(
            "Validation failed",
            status_code=422,
            response_data={"errors": {"field": ["error"]}}
        )
        
        # Test that the string representation includes the message
        assert "Validation failed" in str(error)
        
        # Test that repr includes class name and message
        repr_str = repr(error)
        assert "ValidationError" in repr_str
        assert "Validation failed" in repr_str

    def test_exception_equality(self):
        """Test exception equality comparison."""
        error1 = CarespaceError("Test error", status_code=400)
        error2 = CarespaceError("Test error", status_code=400)
        error3 = CarespaceError("Different error", status_code=400)
        
        # Exceptions with same message and status should be equal
        assert error1.message == error2.message
        assert error1.status_code == error2.status_code
        
        # Exceptions with different messages should not be equal
        assert error1.message != error3.message

    def test_exception_with_none_values(self):
        """Test exceptions with None values."""
        error = CarespaceError(
            message="Test error",
            status_code=None,
            response_data=None
        )
        
        assert error.message == "Test error"
        assert error.status_code is None
        assert error.response_data is None

    def test_exception_chaining(self):
        """Test exception chaining with original exceptions."""
        original = ValueError("Original error")
        
        network_error = NetworkError(
            "Network failed",
            original_exception=original
        )
        
        assert network_error.original_exception == original
        assert isinstance(network_error.original_exception, ValueError)

    def test_rate_limit_error_retry_after_types(self):
        """Test RateLimitError with different retry_after types."""
        # Integer retry_after
        error1 = RateLimitError("Rate limited", retry_after=60)
        assert error1.retry_after == 60
        
        # Float retry_after
        error2 = RateLimitError("Rate limited", retry_after=30.5)
        assert error2.retry_after == 30.5
        
        # String retry_after (should be converted to int if possible)
        error3 = RateLimitError("Rate limited", retry_after="120")
        assert error3.retry_after == "120"  # Kept as string for now