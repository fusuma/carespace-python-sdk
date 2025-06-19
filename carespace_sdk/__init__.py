"""
Carespace Python SDK

A modern, async-first Python SDK for the Carespace API with full type safety.
"""

__version__ = "1.0.0"
__author__ = "Carespace Team"
__email__ = "developers@carespace.ai"

from .client import CarespaceClient
from .exceptions import (
    CarespaceError,
    AuthenticationError,
    ValidationError,
    NetworkError,
    ServerError,
)
from .models import (
    User,
    Client,
    Program,
    Exercise,
    Address,
    CreateUserRequest,
    CreateClientRequest,
    CreateProgramRequest,
    LoginRequest,
    PaginationParams,
)

__all__ = [
    # Main client
    "CarespaceClient",
    # Exceptions
    "CarespaceError",
    "AuthenticationError",
    "ValidationError", 
    "NetworkError",
    "ServerError",
    # Models
    "User",
    "Client", 
    "Program",
    "Exercise",
    "Address",
    "CreateUserRequest",
    "CreateClientRequest",
    "CreateProgramRequest",
    "LoginRequest",
    "PaginationParams",
]