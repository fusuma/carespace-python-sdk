"""
Tests for users API endpoints.
"""

import pytest
from unittest.mock import AsyncMock

from carespace_sdk.api import UsersAPI
from carespace_sdk.models import (
    User,
    CreateUserRequest,
    UpdateUserRequest,
    UsersListResponse,
    MessageResponse,
)
from carespace_sdk.exceptions import NotFoundError, ValidationError


class TestUsersAPI:
    """Test users API endpoints."""

    @pytest.mark.asyncio
    async def test_get_users(self, mock_http_client, sample_user_data, sample_paginated_response):
        """Test getting users list."""
        mock_http_client.get.return_value = sample_paginated_response([sample_user_data])
        users_api = UsersAPI(mock_http_client)

        response = await users_api.get_users(page=1, limit=20, search="test")

        assert isinstance(response, UsersListResponse)
        assert len(response.data) == 1
        assert response.data[0].email == "test@example.com"
        assert response.total == 1
        assert response.page == 1

        # Verify request parameters
        mock_http_client.get.assert_called_once_with(
            "/users",
            {"page": 1, "limit": 20, "search": "test"}
        )

    @pytest.mark.asyncio
    async def test_get_users_with_filters(self, mock_http_client, sample_user_data, sample_paginated_response):
        """Test getting users with all filters."""
        mock_http_client.get.return_value = sample_paginated_response([sample_user_data])
        users_api = UsersAPI(mock_http_client)

        response = await users_api.get_users(
            page=2,
            limit=50,
            search="doctor",
            role="doctor",
            is_active=True,
            sort_by="created_at",
            sort_order="desc"
        )

        mock_http_client.get.assert_called_once_with(
            "/users",
            {
                "page": 2,
                "limit": 50,
                "search": "doctor",
                "role": "doctor",
                "is_active": True,
                "sort_by": "created_at",
                "sort_order": "desc"
            }
        )

    @pytest.mark.asyncio
    async def test_get_user(self, mock_http_client, sample_user_data):
        """Test getting a specific user."""
        mock_http_client.get.return_value = sample_user_data
        users_api = UsersAPI(mock_http_client)

        user = await users_api.get_user("user-123")

        assert isinstance(user, User)
        assert user.id == "user-123"
        assert user.email == "test@example.com"
        mock_http_client.get.assert_called_once_with("/users/user-123")

    @pytest.mark.asyncio
    async def test_get_user_not_found(self, mock_http_client):
        """Test getting a non-existent user."""
        mock_http_client.get.side_effect = NotFoundError(
            "User not found",
            status_code=404
        )
        users_api = UsersAPI(mock_http_client)

        with pytest.raises(NotFoundError) as exc_info:
            await users_api.get_user("non-existent")

        assert exc_info.value.status_code == 404

    @pytest.mark.asyncio
    async def test_create_user(self, mock_http_client, sample_user_data):
        """Test creating a user."""
        mock_http_client.post.return_value = sample_user_data
        users_api = UsersAPI(mock_http_client)

        user_data = CreateUserRequest(
            email="test@example.com",
            name="Test User",
            first_name="Test",
            last_name="User",
            role="user",
            password="secure-password"
        )

        user = await users_api.create_user(user_data)

        assert isinstance(user, User)
        assert user.email == "test@example.com"
        mock_http_client.post.assert_called_once_with("/users", user_data)

    @pytest.mark.asyncio
    async def test_update_user(self, mock_http_client, sample_user_data):
        """Test updating a user."""
        updated_data = {**sample_user_data, "name": "Updated User"}
        mock_http_client.put.return_value = updated_data
        users_api = UsersAPI(mock_http_client)

        update_data = UpdateUserRequest(name="Updated User", is_active=True)
        user = await users_api.update_user("user-123", update_data)

        assert isinstance(user, User)
        assert user.name == "Updated User"
        mock_http_client.put.assert_called_once_with("/users/user-123", update_data)

    @pytest.mark.asyncio
    async def test_delete_user(self, mock_http_client):
        """Test deleting a user."""
        mock_http_client.delete.return_value = {"message": "User deleted successfully"}
        users_api = UsersAPI(mock_http_client)

        response = await users_api.delete_user("user-123")

        assert isinstance(response, MessageResponse)
        assert "deleted successfully" in response.message
        mock_http_client.delete.assert_called_once_with("/users/user-123")

    @pytest.mark.asyncio
    async def test_get_user_profile(self, mock_http_client, sample_user_data):
        """Test getting current user profile."""
        mock_http_client.get.return_value = sample_user_data
        users_api = UsersAPI(mock_http_client)

        user = await users_api.get_user_profile()

        assert isinstance(user, User)
        assert user.email == "test@example.com"
        mock_http_client.get.assert_called_once_with("/users/me")

    @pytest.mark.asyncio
    async def test_update_user_profile(self, mock_http_client, sample_user_data):
        """Test updating current user profile."""
        updated_data = {**sample_user_data, "name": "Updated Profile"}
        mock_http_client.put.return_value = updated_data
        users_api = UsersAPI(mock_http_client)

        update_data = UpdateUserRequest(name="Updated Profile")
        user = await users_api.update_user_profile(update_data)

        assert isinstance(user, User)
        assert user.name == "Updated Profile"
        mock_http_client.put.assert_called_once_with("/users/me", update_data)

    @pytest.mark.asyncio
    async def test_get_user_settings(self, mock_http_client):
        """Test getting user settings."""
        settings = {"theme": "dark", "notifications": True}
        mock_http_client.get.return_value = settings
        users_api = UsersAPI(mock_http_client)

        result = await users_api.get_user_settings("user-123")

        assert result == settings
        mock_http_client.get.assert_called_once_with("/users/user-123/settings")

    @pytest.mark.asyncio
    async def test_update_user_settings(self, mock_http_client):
        """Test updating user settings."""
        new_settings = {"theme": "light", "notifications": False}
        mock_http_client.put.return_value = new_settings
        users_api = UsersAPI(mock_http_client)

        result = await users_api.update_user_settings("user-123", new_settings)

        assert result == new_settings
        mock_http_client.put.assert_called_once_with(
            "/users/user-123/settings",
            new_settings
        )

    @pytest.mark.asyncio
    async def test_validation_error(self, mock_http_client):
        """Test validation error when creating user."""
        mock_http_client.post.side_effect = ValidationError(
            "Invalid user data",
            status_code=422,
            response_data={"errors": {"email": ["Email already exists"]}}
        )
        users_api = UsersAPI(mock_http_client)

        user_data = CreateUserRequest(
            email="existing@example.com",
            name="Test User"
        )

        with pytest.raises(ValidationError) as exc_info:
            await users_api.create_user(user_data)

        assert exc_info.value.status_code == 422
        assert "email" in exc_info.value.response_data["errors"]