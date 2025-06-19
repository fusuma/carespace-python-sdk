"""
Pytest configuration and shared fixtures.
"""

import pytest
import asyncio
from typing import AsyncGenerator
from unittest.mock import AsyncMock, MagicMock

from carespace_sdk import CarespaceClient
from carespace_sdk.http_client import HTTPClient


@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
def mock_http_client():
    """Create a mock HTTP client for testing."""
    mock = AsyncMock(spec=HTTPClient)
    mock.base_url = "https://api-dev.carespace.ai"
    mock.api_key = "test-api-key"
    mock.close = AsyncMock()
    return mock


@pytest.fixture
async def client(mock_http_client) -> AsyncGenerator[CarespaceClient, None]:
    """Create a Carespace client with mocked HTTP client."""
    client = CarespaceClient(api_key="test-api-key")
    # Replace the HTTP client with our mock
    client._http_client = mock_http_client
    client.auth._http_client = mock_http_client
    client.users._http_client = mock_http_client
    client.clients._http_client = mock_http_client
    client.programs._http_client = mock_http_client
    yield client
    await client.close()


@pytest.fixture
def sample_user_data():
    """Sample user data for testing."""
    return {
        "id": "user-123",
        "email": "test@example.com",
        "name": "Test User",
        "first_name": "Test",
        "last_name": "User",
        "role": "user",
        "is_active": True,
        "is_verified": True,
        "created_at": "2024-01-01T00:00:00Z",
        "updated_at": "2024-01-01T00:00:00Z"
    }


@pytest.fixture
def sample_client_data():
    """Sample client data for testing."""
    return {
        "id": "client-123",
        "name": "John Doe",
        "email": "john@example.com",
        "phone": "+1234567890",
        "date_of_birth": "1990-01-01",
        "gender": "male",
        "address": {
            "street": "123 Main St",
            "city": "New York",
            "state": "NY",
            "zip_code": "10001",
            "country": "USA"
        },
        "is_active": True,
        "created_at": "2024-01-01T00:00:00Z",
        "updated_at": "2024-01-01T00:00:00Z"
    }


@pytest.fixture
def sample_program_data():
    """Sample program data for testing."""
    return {
        "id": "program-123",
        "name": "Test Program",
        "description": "A test rehabilitation program",
        "category": "rehabilitation",
        "difficulty": "intermediate",
        "duration": 45,
        "is_template": False,
        "exercises": [],
        "created_at": "2024-01-01T00:00:00Z",
        "updated_at": "2024-01-01T00:00:00Z"
    }


@pytest.fixture
def sample_exercise_data():
    """Sample exercise data for testing."""
    return {
        "id": "exercise-123",
        "name": "Test Exercise",
        "description": "A test exercise",
        "instructions": "Perform the exercise as shown",
        "video_url": "https://example.com/video.mp4",
        "duration": 30,
        "repetitions": 10,
        "sets": 3,
        "rest_time": 60,
        "order": 1,
        "created_at": "2024-01-01T00:00:00Z",
        "updated_at": "2024-01-01T00:00:00Z"
    }


@pytest.fixture
def sample_login_response():
    """Sample login response data."""
    return {
        "access_token": "test-access-token",
        "refresh_token": "test-refresh-token",
        "token_type": "Bearer",
        "expires_in": 3600,
        "user": {
            "id": "user-123",
            "email": "test@example.com",
            "name": "Test User",
            "role": "user"
        }
    }


@pytest.fixture
def sample_paginated_response():
    """Sample paginated response structure."""
    def _make_response(data, total=None):
        if total is None:
            total = len(data)
        return {
            "data": data,
            "total": total,
            "page": 1,
            "limit": 20,
            "pages": (total + 19) // 20  # Calculate pages
        }
    return _make_response