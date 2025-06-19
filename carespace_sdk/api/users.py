"""
Users API endpoints.
"""

from typing import TYPE_CHECKING, Optional

from ..models import (
    User,
    CreateUserRequest,
    UpdateUserRequest,
    UsersListResponse,
    PaginationParams,
    MessageResponse,
)

if TYPE_CHECKING:
    from ..http_client import HTTPClient


class UsersAPI:
    """Users API client."""

    def __init__(self, http_client: "HTTPClient") -> None:
        """Initialize the Users API client."""
        self._http_client = http_client

    async def get_users(
        self,
        page: int = 1,
        limit: int = 20,
        search: Optional[str] = None,
        sort_by: Optional[str] = None,
        sort_order: Optional[str] = "asc",
    ) -> UsersListResponse:
        """
        Get a paginated list of users.

        Args:
            page: Page number (1-based)
            limit: Number of items per page (1-100)
            search: Search query to filter users
            sort_by: Field to sort by
            sort_order: Sort order ('asc' or 'desc')

        Returns:
            UsersListResponse: Paginated list of users

        Raises:
            AuthenticationError: If not authenticated
            ValidationError: If parameters are invalid
            CarespaceError: For other API errors
        """
        params = PaginationParams(
            page=page,
            limit=limit,
            search=search,
            sort_by=sort_by,
            sort_order=sort_order,
        )
        response_data = await self._http_client.get("/users", params.model_dump(exclude_none=True))
        return UsersListResponse.model_validate(response_data)

    async def get_user(self, user_id: str) -> User:
        """
        Get a specific user by ID.

        Args:
            user_id: User ID

        Returns:
            User: User details

        Raises:
            AuthenticationError: If not authenticated
            NotFoundError: If user doesn't exist
            CarespaceError: For other API errors
        """
        response_data = await self._http_client.get(f"/users/{user_id}")
        return User.model_validate(response_data)

    async def create_user(self, user_data: CreateUserRequest) -> User:
        """
        Create a new user.

        Args:
            user_data: User creation data

        Returns:
            User: Created user details

        Raises:
            AuthenticationError: If not authenticated
            ValidationError: If user data is invalid
            CarespaceError: For other API errors
        """
        response_data = await self._http_client.post("/users", user_data)
        return User.model_validate(response_data)

    async def update_user(self, user_id: str, user_data: UpdateUserRequest) -> User:
        """
        Update an existing user.

        Args:
            user_id: User ID
            user_data: User update data

        Returns:
            User: Updated user details

        Raises:
            AuthenticationError: If not authenticated
            NotFoundError: If user doesn't exist
            ValidationError: If user data is invalid
            CarespaceError: For other API errors
        """
        response_data = await self._http_client.put(f"/users/{user_id}", user_data)
        return User.model_validate(response_data)

    async def delete_user(self, user_id: str) -> MessageResponse:
        """
        Delete a user.

        Args:
            user_id: User ID

        Returns:
            MessageResponse: Confirmation message

        Raises:
            AuthenticationError: If not authenticated
            NotFoundError: If user doesn't exist
            CarespaceError: For other API errors
        """
        response_data = await self._http_client.delete(f"/users/{user_id}")
        return MessageResponse.model_validate(response_data)

    async def get_user_profile(self) -> User:
        """
        Get the current authenticated user's profile.

        Returns:
            User: Current user profile

        Raises:
            AuthenticationError: If not authenticated
            CarespaceError: For other API errors
        """
        response_data = await self._http_client.get("/users/profile")
        return User.model_validate(response_data)

    async def update_user_profile(self, user_data: UpdateUserRequest) -> User:
        """
        Update the current authenticated user's profile.

        Args:
            user_data: Profile update data

        Returns:
            User: Updated user profile

        Raises:
            AuthenticationError: If not authenticated
            ValidationError: If user data is invalid
            CarespaceError: For other API errors
        """
        response_data = await self._http_client.put("/users/profile", user_data)
        return User.model_validate(response_data)

    async def get_user_settings(self, user_id: str) -> dict:
        """
        Get user settings.

        Args:
            user_id: User ID

        Returns:
            dict: User settings

        Raises:
            AuthenticationError: If not authenticated
            NotFoundError: If user doesn't exist
            CarespaceError: For other API errors
        """
        return await self._http_client.get(f"/users/{user_id}/settings")

    async def update_user_settings(self, user_id: str, settings: dict) -> dict:
        """
        Update user settings.

        Args:
            user_id: User ID
            settings: Settings to update

        Returns:
            dict: Updated user settings

        Raises:
            AuthenticationError: If not authenticated
            NotFoundError: If user doesn't exist
            ValidationError: If settings are invalid
            CarespaceError: For other API errors
        """
        return await self._http_client.put(f"/users/{user_id}/settings", settings)