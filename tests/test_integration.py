"""
Integration tests for the Carespace SDK.

These tests use real HTTP requests but against a mock server.
They test the full flow from client initialization to API calls.
"""

import pytest
import asyncio
from unittest.mock import patch, AsyncMock

from carespace_sdk import CarespaceClient, create_production_client
from carespace_sdk.models import CreateUserRequest, CreateClientRequest, Address
from carespace_sdk.exceptions import AuthenticationError, NotFoundError


@pytest.mark.integration
class TestSDKIntegration:
    """Integration tests for the complete SDK flow."""

    @pytest.mark.asyncio
    async def test_full_authentication_flow(self):
        """Test complete authentication flow."""
        login_response = {
            "access_token": "test-token",
            "refresh_token": "refresh-token",
            "token_type": "Bearer",
            "expires_in": 3600,
            "user": {
                "id": "user-123",
                "email": "test@example.com",
                "name": "Test User",
                "role": "admin"
            }
        }
        
        refresh_response = {
            "access_token": "new-token",
            "refresh_token": "new-refresh-token",
            "token_type": "Bearer",
            "expires_in": 3600
        }

        with patch('httpx.AsyncClient') as mock_client_class:
            mock_client = AsyncMock()
            
            # Mock login response
            mock_login_response = AsyncMock()
            mock_login_response.status_code = 200
            mock_login_response.json.return_value = login_response
            mock_login_response.raise_for_status = AsyncMock()
            
            # Mock refresh response
            mock_refresh_response = AsyncMock()
            mock_refresh_response.status_code = 200
            mock_refresh_response.json.return_value = refresh_response
            mock_refresh_response.raise_for_status = AsyncMock()
            
            # Mock logout response
            mock_logout_response = AsyncMock()
            mock_logout_response.status_code = 200
            mock_logout_response.json.return_value = {"message": "Logged out"}
            mock_logout_response.raise_for_status = AsyncMock()
            
            mock_client.post.side_effect = [
                mock_login_response,
                mock_refresh_response,
                mock_logout_response
            ]
            mock_client_class.return_value = mock_client

            async with CarespaceClient() as client:
                # Login
                login_result = await client.login_and_set_token(
                    "test@example.com", 
                    "password"
                )
                assert login_result.access_token == "test-token"
                assert client.api_key == "test-token"

                # Refresh token
                refresh_result = await client.auth.refresh_token("refresh-token")
                assert refresh_result.access_token == "new-token"

                # Logout
                logout_result = await client.auth.logout()
                assert "Logged out" in logout_result.message

    @pytest.mark.asyncio
    async def test_user_management_flow(self):
        """Test complete user management flow."""
        user_data = {
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

        users_list = {
            "data": [user_data],
            "total": 1,
            "page": 1,
            "limit": 20,
            "pages": 1
        }

        with patch('httpx.AsyncClient') as mock_client_class:
            mock_client = AsyncMock()
            
            # Mock responses
            mock_get_response = AsyncMock()
            mock_get_response.status_code = 200
            mock_get_response.json.return_value = users_list
            mock_get_response.raise_for_status = AsyncMock()
            
            mock_get_user_response = AsyncMock()
            mock_get_user_response.status_code = 200
            mock_get_user_response.json.return_value = user_data
            mock_get_user_response.raise_for_status = AsyncMock()
            
            mock_create_response = AsyncMock()
            mock_create_response.status_code = 201
            mock_create_response.json.return_value = user_data
            mock_create_response.raise_for_status = AsyncMock()
            
            mock_update_response = AsyncMock()
            updated_user = {**user_data, "name": "Updated User"}
            mock_update_response.status_code = 200
            mock_update_response.json.return_value = updated_user
            mock_update_response.raise_for_status = AsyncMock()
            
            mock_delete_response = AsyncMock()
            mock_delete_response.status_code = 200
            mock_delete_response.json.return_value = {"message": "User deleted"}
            mock_delete_response.raise_for_status = AsyncMock()
            
            mock_client.get.side_effect = [mock_get_response, mock_get_user_response]
            mock_client.post.return_value = mock_create_response
            mock_client.put.return_value = mock_update_response
            mock_client.delete.return_value = mock_delete_response
            mock_client_class.return_value = mock_client

            async with CarespaceClient(api_key="test-key") as client:
                # Get users
                users_response = await client.users.get_users(limit=20)
                assert len(users_response.data) == 1
                assert users_response.data[0].email == "test@example.com"

                # Get specific user
                user = await client.users.get_user("user-123")
                assert user.id == "user-123"
                assert user.email == "test@example.com"

                # Create user
                create_request = CreateUserRequest(
                    email="new@example.com",
                    name="New User",
                    password="secure-password"
                )
                created_user = await client.users.create_user(create_request)
                assert created_user.email == "test@example.com"

                # Update user
                from carespace_sdk.models import UpdateUserRequest
                update_request = UpdateUserRequest(name="Updated User")
                updated_user = await client.users.update_user("user-123", update_request)

                # Delete user
                delete_result = await client.users.delete_user("user-123")
                assert "deleted" in delete_result.message

    @pytest.mark.asyncio
    async def test_client_management_flow(self):
        """Test complete client management flow."""
        client_data = {
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

        stats_data = {
            "total_sessions": 5,
            "completed_exercises": 20,
            "average_score": 88.5,
            "last_session_date": "2024-01-15T10:30:00Z",
            "progress_percentage": 80.0
        }

        with patch('httpx.AsyncClient') as mock_client_class:
            mock_client = AsyncMock()
            
            # Mock create client response
            mock_create_response = AsyncMock()
            mock_create_response.status_code = 201
            mock_create_response.json.return_value = client_data
            mock_create_response.raise_for_status = AsyncMock()
            
            # Mock get client response
            mock_get_response = AsyncMock()
            mock_get_response.status_code = 200
            mock_get_response.json.return_value = client_data
            mock_get_response.raise_for_status = AsyncMock()
            
            # Mock stats response
            mock_stats_response = AsyncMock()
            mock_stats_response.status_code = 200
            mock_stats_response.json.return_value = stats_data
            mock_stats_response.raise_for_status = AsyncMock()
            
            mock_client.post.return_value = mock_create_response
            mock_client.get.side_effect = [mock_get_response, mock_stats_response]
            mock_client_class.return_value = mock_client

            async with CarespaceClient(api_key="test-key") as client:
                # Create client
                address = Address(
                    street="123 Main St",
                    city="New York",
                    state="NY",
                    zip_code="10001"
                )
                
                create_request = CreateClientRequest(
                    name="John Doe",
                    email="john@example.com",
                    phone="+1234567890",
                    address=address
                )
                
                created_client = await client.clients.create_client(create_request)
                assert created_client.name == "John Doe"
                assert created_client.address.street == "123 Main St"

                # Get client
                retrieved_client = await client.clients.get_client("client-123")
                assert retrieved_client.id == "client-123"

                # Get client stats
                stats = await client.clients.get_client_stats("client-123")
                assert stats.total_sessions == 5
                assert stats.average_score == 88.5

    @pytest.mark.asyncio
    async def test_error_handling_flow(self):
        """Test error handling across the SDK."""
        with patch('httpx.AsyncClient') as mock_client_class:
            mock_client = AsyncMock()
            
            # Mock 401 response
            mock_401_response = AsyncMock()
            mock_401_response.status_code = 401
            mock_401_response.json.return_value = {"error": "Unauthorized"}
            
            # Mock 404 response
            mock_404_response = AsyncMock()
            mock_404_response.status_code = 404
            mock_404_response.json.return_value = {"error": "Not found"}
            
            import httpx
            mock_client.get.side_effect = [
                httpx.HTTPStatusError(
                    "401 Unauthorized",
                    request=AsyncMock(),
                    response=mock_401_response
                ),
                httpx.HTTPStatusError(
                    "404 Not Found",
                    request=AsyncMock(),
                    response=mock_404_response
                )
            ]
            mock_client_class.return_value = mock_client

            async with CarespaceClient() as client:
                # Test authentication error
                with pytest.raises(AuthenticationError) as exc_info:
                    await client.users.get_users()
                assert exc_info.value.status_code == 401

                # Test not found error
                with pytest.raises(NotFoundError) as exc_info:
                    await client.users.get_user("non-existent")
                assert exc_info.value.status_code == 404

    @pytest.mark.asyncio
    async def test_health_check_flow(self):
        """Test health check functionality."""
        profile_data = {
            "id": "user-123",
            "email": "test@example.com",
            "name": "Test User",
            "role": "user",
            "is_active": True,
            "is_verified": True,
            "created_at": "2024-01-01T00:00:00Z",
            "updated_at": "2024-01-01T00:00:00Z"
        }

        with patch('httpx.AsyncClient') as mock_client_class:
            mock_client = AsyncMock()
            
            # Mock successful profile response
            mock_response = AsyncMock()
            mock_response.status_code = 200
            mock_response.json.return_value = profile_data
            mock_response.raise_for_status = AsyncMock()
            
            mock_client.get.return_value = mock_response
            mock_client_class.return_value = mock_client

            async with CarespaceClient(api_key="test-key") as client:
                # Health check should succeed
                is_healthy = await client.health_check()
                assert is_healthy is True

    @pytest.mark.asyncio
    async def test_production_client_configuration(self):
        """Test production client factory."""
        user_data = {
            "id": "user-123",
            "email": "prod@example.com",
            "name": "Production User",
            "role": "admin",
            "is_active": True,
            "is_verified": True,
            "created_at": "2024-01-01T00:00:00Z",
            "updated_at": "2024-01-01T00:00:00Z"
        }

        with patch('httpx.AsyncClient') as mock_client_class:
            mock_client = AsyncMock()
            
            mock_response = AsyncMock()
            mock_response.status_code = 200
            mock_response.json.return_value = user_data
            mock_response.raise_for_status = AsyncMock()
            
            mock_client.get.return_value = mock_response
            mock_client_class.return_value = mock_client

            # Test production client
            async with create_production_client("prod-api-key") as client:
                assert client.base_url == "https://api.carespace.ai"
                assert client.api_key == "prod-api-key"
                
                # Make a request to verify configuration
                profile = await client.users.get_user_profile()
                assert profile.email == "prod@example.com"

    @pytest.mark.asyncio
    async def test_concurrent_requests(self):
        """Test handling multiple concurrent requests."""
        user_data = {
            "id": "user-123",
            "email": "test@example.com",
            "name": "Test User",
            "role": "user",
            "is_active": True,
            "is_verified": True,
            "created_at": "2024-01-01T00:00:00Z",
            "updated_at": "2024-01-01T00:00:00Z"
        }

        with patch('httpx.AsyncClient') as mock_client_class:
            mock_client = AsyncMock()
            
            mock_response = AsyncMock()
            mock_response.status_code = 200
            mock_response.json.return_value = user_data
            mock_response.raise_for_status = AsyncMock()
            
            mock_client.get.return_value = mock_response
            mock_client_class.return_value = mock_client

            async with CarespaceClient(api_key="test-key") as client:
                # Make multiple concurrent requests
                tasks = [
                    client.users.get_user("user-1"),
                    client.users.get_user("user-2"),
                    client.users.get_user("user-3"),
                ]
                
                results = await asyncio.gather(*tasks)
                
                # All requests should succeed
                assert len(results) == 3
                for result in results:
                    assert result.email == "test@example.com"
                
                # Verify all requests were made
                assert mock_client.get.call_count == 3