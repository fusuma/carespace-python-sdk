"""
Tests for the main CarespaceClient class.
"""

import pytest
from unittest.mock import AsyncMock, patch

from carespace_sdk import (
    CarespaceClient,
    create_client,
    create_production_client,
    create_development_client,
)
from carespace_sdk.models import LoginResponse


class TestCarespaceClient:
    """Test the main CarespaceClient class."""

    def test_client_initialization(self):
        """Test client initialization with different parameters."""
        # Default initialization
        client = CarespaceClient()
        assert client.base_url == "https://api-dev.carespace.ai"
        assert client.api_key is None

        # With API key
        client = CarespaceClient(api_key="test-key")
        assert client.api_key == "test-key"

        # With custom base URL
        client = CarespaceClient(base_url="https://custom.api.com")
        assert client.base_url == "https://custom.api.com"

    @pytest.mark.asyncio
    async def test_context_manager(self):
        """Test async context manager support."""
        async with CarespaceClient(api_key="test-key") as client:
            assert isinstance(client, CarespaceClient)
            assert client.api_key == "test-key"

    @pytest.mark.asyncio
    async def test_set_api_key(self, client):
        """Test setting API key."""
        client.set_api_key("new-api-key")
        client._http_client.set_api_key.assert_called_once_with("new-api-key")

    @pytest.mark.asyncio
    async def test_login_and_set_token(self, client, sample_login_response):
        """Test login and automatic token setting."""
        client._http_client.post.return_value = sample_login_response

        response = await client.login_and_set_token("test@example.com", "password")

        assert isinstance(response, LoginResponse)
        assert response.access_token == "test-access-token"
        client._http_client.set_api_key.assert_called_with("test-access-token")

    @pytest.mark.asyncio
    async def test_quick_get_users(self, client, sample_user_data, sample_paginated_response):
        """Test quick_get_users convenience method."""
        client._http_client.get.return_value = sample_paginated_response([sample_user_data])

        response = await client.quick_get_users(limit=10, search="test")

        client._http_client.get.assert_called_once()
        assert len(response.data) == 1
        assert response.data[0].email == "test@example.com"

    @pytest.mark.asyncio
    async def test_quick_get_clients(self, client, sample_client_data, sample_paginated_response):
        """Test quick_get_clients convenience method."""
        client._http_client.get.return_value = sample_paginated_response([sample_client_data])

        response = await client.quick_get_clients(limit=10, search="john")

        client._http_client.get.assert_called_once()
        assert len(response.data) == 1
        assert response.data[0].name == "John Doe"

    @pytest.mark.asyncio
    async def test_quick_get_programs(self, client, sample_program_data, sample_paginated_response):
        """Test quick_get_programs convenience method."""
        client._http_client.get.return_value = sample_paginated_response([sample_program_data])

        response = await client.quick_get_programs(limit=10, category="rehabilitation")

        client._http_client.get.assert_called_once()
        assert len(response.data) == 1
        assert response.data[0].name == "Test Program"

    @pytest.mark.asyncio
    async def test_health_check_with_auth(self, client, sample_user_data):
        """Test health check with authentication."""
        client._http_client.api_key = "test-key"
        client._http_client.get.return_value = sample_user_data

        result = await client.health_check()

        assert result is True
        client._http_client.get.assert_called_once()

    @pytest.mark.asyncio
    async def test_health_check_without_auth(self, client, sample_user_data, sample_paginated_response):
        """Test health check without authentication."""
        client._http_client.api_key = None
        client._http_client.get.return_value = sample_paginated_response([sample_user_data])

        result = await client.health_check()

        assert result is True
        client._http_client.get.assert_called_once()

    @pytest.mark.asyncio
    async def test_health_check_failure(self, client):
        """Test health check when API is unreachable."""
        client._http_client.get.side_effect = Exception("Network error")

        result = await client.health_check()

        assert result is False


class TestClientFactories:
    """Test client factory functions."""

    def test_create_client(self):
        """Test create_client factory."""
        client = create_client(api_key="test-key")
        assert isinstance(client, CarespaceClient)
        assert client.api_key == "test-key"
        assert client.base_url == "https://api-dev.carespace.ai"

    def test_create_production_client(self):
        """Test create_production_client factory."""
        client = create_production_client(api_key="prod-key")
        assert isinstance(client, CarespaceClient)
        assert client.api_key == "prod-key"
        assert client.base_url == "https://api.carespace.ai"

    def test_create_development_client(self):
        """Test create_development_client factory."""
        client = create_development_client(api_key="dev-key")
        assert isinstance(client, CarespaceClient)
        assert client.api_key == "dev-key"
        assert client.base_url == "https://api-dev.carespace.ai"