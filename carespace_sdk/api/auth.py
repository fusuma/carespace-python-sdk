"""
Authentication API endpoints.
"""

from typing import TYPE_CHECKING

from ..models import (
    LoginRequest,
    LoginResponse,
    RefreshTokenRequest,
    MessageResponse,
)

if TYPE_CHECKING:
    from ..http_client import HTTPClient


class AuthAPI:
    """Authentication API client."""

    def __init__(self, http_client: "HTTPClient") -> None:
        """Initialize the Auth API client."""
        self._http_client = http_client

    async def login(self, email: str, password: str) -> LoginResponse:
        """
        Authenticate a user and get access tokens.

        Args:
            email: User email address
            password: User password

        Returns:
            LoginResponse: Authentication tokens and user info

        Raises:
            AuthenticationError: If credentials are invalid
            ValidationError: If email or password format is invalid
            CarespaceError: For other API errors
        """
        request = LoginRequest(email=email, password=password)
        response_data = await self._http_client.post("/auth/login", request)
        return LoginResponse.model_validate(response_data)

    async def logout(self) -> MessageResponse:
        """
        Logout the current user (invalidate tokens).

        Returns:
            MessageResponse: Confirmation message

        Raises:
            AuthenticationError: If not authenticated
            CarespaceError: For other API errors
        """
        response_data = await self._http_client.post("/auth/logout")
        return MessageResponse.model_validate(response_data)

    async def refresh_token(self, refresh_token: str) -> LoginResponse:
        """
        Refresh access token using refresh token.

        Args:
            refresh_token: Valid refresh token

        Returns:
            LoginResponse: New authentication tokens

        Raises:
            AuthenticationError: If refresh token is invalid or expired
            CarespaceError: For other API errors
        """
        request = RefreshTokenRequest(refresh_token=refresh_token)
        response_data = await self._http_client.post("/auth/refresh", request)
        return LoginResponse.model_validate(response_data)

    async def forgot_password(self, email: str) -> MessageResponse:
        """
        Request password reset for user.

        Args:
            email: User email address

        Returns:
            MessageResponse: Confirmation message

        Raises:
            ValidationError: If email format is invalid
            NotFoundError: If user with email doesn't exist
            CarespaceError: For other API errors
        """
        request_data = {"email": email}
        response_data = await self._http_client.post("/auth/forgot-password", request_data)
        return MessageResponse.model_validate(response_data)

    async def reset_password(self, token: str, password: str) -> MessageResponse:
        """
        Reset password using reset token.

        Args:
            token: Password reset token
            password: New password

        Returns:
            MessageResponse: Confirmation message

        Raises:
            AuthenticationError: If reset token is invalid or expired
            ValidationError: If password doesn't meet requirements
            CarespaceError: For other API errors
        """
        request_data = {"token": token, "password": password}
        response_data = await self._http_client.post("/auth/reset-password", request_data)
        return MessageResponse.model_validate(response_data)

    async def change_password(self, current_password: str, new_password: str) -> MessageResponse:
        """
        Change password for authenticated user.

        Args:
            current_password: Current password
            new_password: New password

        Returns:
            MessageResponse: Confirmation message

        Raises:
            AuthenticationError: If current password is incorrect or not authenticated
            ValidationError: If new password doesn't meet requirements
            CarespaceError: For other API errors
        """
        request_data = {
            "current_password": current_password,
            "new_password": new_password,
        }
        response_data = await self._http_client.post("/auth/change-password", request_data)
        return MessageResponse.model_validate(response_data)

    async def verify_email(self, token: str) -> MessageResponse:
        """
        Verify email address using verification token.

        Args:
            token: Email verification token

        Returns:
            MessageResponse: Confirmation message

        Raises:
            AuthenticationError: If verification token is invalid or expired
            CarespaceError: For other API errors
        """
        request_data = {"token": token}
        response_data = await self._http_client.post("/auth/verify-email", request_data)
        return MessageResponse.model_validate(response_data)

    async def resend_verification(self, email: str) -> MessageResponse:
        """
        Resend email verification.

        Args:
            email: User email address

        Returns:
            MessageResponse: Confirmation message

        Raises:
            ValidationError: If email format is invalid
            NotFoundError: If user with email doesn't exist
            CarespaceError: For other API errors
        """
        request_data = {"email": email}
        response_data = await self._http_client.post("/auth/resend-verification", request_data)
        return MessageResponse.model_validate(response_data)