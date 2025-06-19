"""
Tests for authentication API endpoints.
"""

import pytest
from unittest.mock import AsyncMock

from carespace_sdk.api import AuthAPI
from carespace_sdk.models import (
    LoginRequest,
    LoginResponse,
    TokenRefreshRequest,
    TokenRefreshResponse,
    MessageResponse,
    SuccessResponse,
)
from carespace_sdk.exceptions import AuthenticationError, ValidationError


class TestAuthAPI:
    """Test authentication API endpoints."""

    @pytest.mark.asyncio
    async def test_login_success(self, mock_http_client, sample_login_response):
        """Test successful login."""
        mock_http_client.post.return_value = sample_login_response
        auth_api = AuthAPI(mock_http_client)

        response = await auth_api.login("test@example.com", "password")

        assert isinstance(response, LoginResponse)
        assert response.access_token == "test-access-token"
        assert response.refresh_token == "test-refresh-token"
        assert response.user.email == "test@example.com"

        # Verify the request
        mock_http_client.post.assert_called_once_with(
            "/auth/login",
            LoginRequest(email="test@example.com", password="password")
        )

    @pytest.mark.asyncio
    async def test_login_invalid_credentials(self, mock_http_client):
        """Test login with invalid credentials."""
        mock_http_client.post.side_effect = AuthenticationError(
            "Invalid credentials",
            status_code=401
        )
        auth_api = AuthAPI(mock_http_client)

        with pytest.raises(AuthenticationError) as exc_info:
            await auth_api.login("test@example.com", "wrong-password")

        assert exc_info.value.status_code == 401
        assert "Invalid credentials" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_logout(self, mock_http_client):
        """Test logout."""
        mock_http_client.post.return_value = {"message": "Logged out successfully"}
        auth_api = AuthAPI(mock_http_client)

        response = await auth_api.logout()

        assert isinstance(response, MessageResponse)
        assert response.message == "Logged out successfully"
        mock_http_client.post.assert_called_once_with("/auth/logout", {})

    @pytest.mark.asyncio
    async def test_refresh_token(self, mock_http_client):
        """Test token refresh."""
        refresh_response = {
            "access_token": "new-access-token",
            "refresh_token": "new-refresh-token",
            "token_type": "Bearer",
            "expires_in": 3600
        }
        mock_http_client.post.return_value = refresh_response
        auth_api = AuthAPI(mock_http_client)

        response = await auth_api.refresh_token("old-refresh-token")

        assert isinstance(response, TokenRefreshResponse)
        assert response.access_token == "new-access-token"
        assert response.refresh_token == "new-refresh-token"

        mock_http_client.post.assert_called_once_with(
            "/auth/refresh",
            TokenRefreshRequest(refresh_token="old-refresh-token")
        )

    @pytest.mark.asyncio
    async def test_forgot_password(self, mock_http_client):
        """Test forgot password."""
        mock_http_client.post.return_value = {
            "message": "Password reset email sent"
        }
        auth_api = AuthAPI(mock_http_client)

        response = await auth_api.forgot_password("test@example.com")

        assert isinstance(response, MessageResponse)
        assert "Password reset email sent" in response.message

        mock_http_client.post.assert_called_once_with(
            "/auth/forgot-password",
            {"email": "test@example.com"}
        )

    @pytest.mark.asyncio
    async def test_reset_password(self, mock_http_client):
        """Test password reset."""
        mock_http_client.post.return_value = {
            "message": "Password reset successfully"
        }
        auth_api = AuthAPI(mock_http_client)

        response = await auth_api.reset_password("reset-token", "new-password")

        assert isinstance(response, MessageResponse)
        assert "Password reset successfully" in response.message

        mock_http_client.post.assert_called_once_with(
            "/auth/reset-password",
            {"token": "reset-token", "password": "new-password"}
        )

    @pytest.mark.asyncio
    async def test_change_password(self, mock_http_client):
        """Test password change."""
        mock_http_client.post.return_value = {
            "message": "Password changed successfully"
        }
        auth_api = AuthAPI(mock_http_client)

        response = await auth_api.change_password("old-password", "new-password")

        assert isinstance(response, MessageResponse)
        assert "Password changed successfully" in response.message

        mock_http_client.post.assert_called_once_with(
            "/auth/change-password",
            {"current_password": "old-password", "new_password": "new-password"}
        )

    @pytest.mark.asyncio
    async def test_verify_email(self, mock_http_client):
        """Test email verification."""
        mock_http_client.post.return_value = {"success": True}
        auth_api = AuthAPI(mock_http_client)

        response = await auth_api.verify_email("verification-token")

        assert isinstance(response, SuccessResponse)
        assert response.success is True

        mock_http_client.post.assert_called_once_with(
            "/auth/verify-email",
            {"token": "verification-token"}
        )

    @pytest.mark.asyncio
    async def test_resend_verification(self, mock_http_client):
        """Test resend verification email."""
        mock_http_client.post.return_value = {
            "message": "Verification email sent"
        }
        auth_api = AuthAPI(mock_http_client)

        response = await auth_api.resend_verification("test@example.com")

        assert isinstance(response, MessageResponse)
        assert "Verification email sent" in response.message

        mock_http_client.post.assert_called_once_with(
            "/auth/resend-verification",
            {"email": "test@example.com"}
        )

    @pytest.mark.asyncio
    async def test_validation_error(self, mock_http_client):
        """Test validation error handling."""
        mock_http_client.post.side_effect = ValidationError(
            "Invalid email format",
            status_code=422,
            response_data={"errors": {"email": ["Invalid email format"]}}
        )
        auth_api = AuthAPI(mock_http_client)

        with pytest.raises(ValidationError) as exc_info:
            await auth_api.login("invalid-email", "password")

        assert exc_info.value.status_code == 422
        assert "Invalid email format" in str(exc_info.value)
        assert "email" in exc_info.value.response_data["errors"]