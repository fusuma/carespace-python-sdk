"""
Clients API endpoints.
"""

from typing import TYPE_CHECKING, Optional

from ..models import (
    Client,
    CreateClientRequest,
    UpdateClientRequest,
    ClientsListResponse,
    ClientStats,
    ProgramsListResponse,
    PaginationParams,
    MessageResponse,
    SuccessResponse,
)

if TYPE_CHECKING:
    from ..http_client import HTTPClient


class ClientsAPI:
    """Clients API client."""

    def __init__(self, http_client: "HTTPClient") -> None:
        """Initialize the Clients API client."""
        self._http_client = http_client

    async def get_clients(
        self,
        page: int = 1,
        limit: int = 20,
        search: Optional[str] = None,
        sort_by: Optional[str] = None,
        sort_order: Optional[str] = "asc",
    ) -> ClientsListResponse:
        """
        Get a paginated list of clients.

        Args:
            page: Page number (1-based)
            limit: Number of items per page (1-100)
            search: Search query to filter clients
            sort_by: Field to sort by
            sort_order: Sort order ('asc' or 'desc')

        Returns:
            ClientsListResponse: Paginated list of clients

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
        response_data = await self._http_client.get("/clients", params.model_dump(exclude_none=True))
        return ClientsListResponse.model_validate(response_data)

    async def get_client(self, client_id: str) -> Client:
        """
        Get a specific client by ID.

        Args:
            client_id: Client ID

        Returns:
            Client: Client details

        Raises:
            AuthenticationError: If not authenticated
            NotFoundError: If client doesn't exist
            CarespaceError: For other API errors
        """
        response_data = await self._http_client.get(f"/clients/{client_id}")
        return Client.model_validate(response_data)

    async def create_client(self, client_data: CreateClientRequest) -> Client:
        """
        Create a new client.

        Args:
            client_data: Client creation data

        Returns:
            Client: Created client details

        Raises:
            AuthenticationError: If not authenticated
            ValidationError: If client data is invalid
            CarespaceError: For other API errors
        """
        response_data = await self._http_client.post("/clients", client_data)
        return Client.model_validate(response_data)

    async def update_client(self, client_id: str, client_data: UpdateClientRequest) -> Client:
        """
        Update an existing client.

        Args:
            client_id: Client ID
            client_data: Client update data

        Returns:
            Client: Updated client details

        Raises:
            AuthenticationError: If not authenticated
            NotFoundError: If client doesn't exist
            ValidationError: If client data is invalid
            CarespaceError: For other API errors
        """
        response_data = await self._http_client.put(f"/clients/{client_id}", client_data)
        return Client.model_validate(response_data)

    async def delete_client(self, client_id: str) -> MessageResponse:
        """
        Delete a client.

        Args:
            client_id: Client ID

        Returns:
            MessageResponse: Confirmation message

        Raises:
            AuthenticationError: If not authenticated
            NotFoundError: If client doesn't exist
            CarespaceError: For other API errors
        """
        response_data = await self._http_client.delete(f"/clients/{client_id}")
        return MessageResponse.model_validate(response_data)

    async def get_client_stats(self, client_id: str) -> ClientStats:
        """
        Get statistics for a specific client.

        Args:
            client_id: Client ID

        Returns:
            ClientStats: Client statistics

        Raises:
            AuthenticationError: If not authenticated
            NotFoundError: If client doesn't exist
            CarespaceError: For other API errors
        """
        response_data = await self._http_client.get(f"/clients/{client_id}/stats")
        return ClientStats.model_validate(response_data)

    async def get_client_programs(
        self,
        client_id: str,
        page: int = 1,
        limit: int = 20,
        search: Optional[str] = None,
    ) -> ProgramsListResponse:
        """
        Get programs assigned to a specific client.

        Args:
            client_id: Client ID
            page: Page number (1-based)
            limit: Number of items per page (1-100)
            search: Search query to filter programs

        Returns:
            ProgramsListResponse: Paginated list of client programs

        Raises:
            AuthenticationError: If not authenticated
            NotFoundError: If client doesn't exist
            ValidationError: If parameters are invalid
            CarespaceError: For other API errors
        """
        params = PaginationParams(page=page, limit=limit, search=search)
        response_data = await self._http_client.get(
            f"/clients/{client_id}/programs",
            params.model_dump(exclude_none=True)
        )
        return ProgramsListResponse.model_validate(response_data)

    async def assign_program_to_client(
        self,
        client_id: str,
        program_id: str,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        notes: Optional[str] = None,
    ) -> SuccessResponse:
        """
        Assign a program to a client.

        Args:
            client_id: Client ID
            program_id: Program ID
            start_date: Program start date (ISO format)
            end_date: Program end date (ISO format)
            notes: Assignment notes

        Returns:
            SuccessResponse: Success confirmation

        Raises:
            AuthenticationError: If not authenticated
            NotFoundError: If client or program doesn't exist
            ValidationError: If assignment data is invalid
            CarespaceError: For other API errors
        """
        assignment_data = {}
        if start_date:
            assignment_data["start_date"] = start_date
        if end_date:
            assignment_data["end_date"] = end_date
        if notes:
            assignment_data["notes"] = notes

        response_data = await self._http_client.post(
            f"/clients/{client_id}/programs/{program_id}",
            assignment_data
        )
        return SuccessResponse.model_validate(response_data)

    async def remove_client_program(self, client_id: str, program_id: str) -> MessageResponse:
        """
        Remove a program assignment from a client.

        Args:
            client_id: Client ID
            program_id: Program ID

        Returns:
            MessageResponse: Confirmation message

        Raises:
            AuthenticationError: If not authenticated
            NotFoundError: If client, program, or assignment doesn't exist
            CarespaceError: For other API errors
        """
        response_data = await self._http_client.delete(f"/clients/{client_id}/programs/{program_id}")
        return MessageResponse.model_validate(response_data)