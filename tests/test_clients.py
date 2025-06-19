"""
Tests for clients API endpoints.
"""

import pytest
from unittest.mock import AsyncMock

from carespace_sdk.api import ClientsAPI
from carespace_sdk.models import (
    Client,
    CreateClientRequest,
    UpdateClientRequest,
    ClientsListResponse,
    ClientStats,
    ProgramsListResponse,
    MessageResponse,
    SuccessResponse,
    Address,
)
from carespace_sdk.exceptions import NotFoundError, ValidationError


class TestClientsAPI:
    """Test clients API endpoints."""

    @pytest.mark.asyncio
    async def test_get_clients(self, mock_http_client, sample_client_data, sample_paginated_response):
        """Test getting clients list."""
        mock_http_client.get.return_value = sample_paginated_response([sample_client_data])
        clients_api = ClientsAPI(mock_http_client)

        response = await clients_api.get_clients(page=1, limit=20, search="john")

        assert isinstance(response, ClientsListResponse)
        assert len(response.data) == 1
        assert response.data[0].name == "John Doe"
        assert response.total == 1

        mock_http_client.get.assert_called_once_with(
            "/clients",
            {"page": 1, "limit": 20, "search": "john"}
        )

    @pytest.mark.asyncio
    async def test_get_client(self, mock_http_client, sample_client_data):
        """Test getting a specific client."""
        mock_http_client.get.return_value = sample_client_data
        clients_api = ClientsAPI(mock_http_client)

        client = await clients_api.get_client("client-123")

        assert isinstance(client, Client)
        assert client.id == "client-123"
        assert client.name == "John Doe"
        mock_http_client.get.assert_called_once_with("/clients/client-123")

    @pytest.mark.asyncio
    async def test_create_client(self, mock_http_client, sample_client_data):
        """Test creating a client."""
        mock_http_client.post.return_value = sample_client_data
        clients_api = ClientsAPI(mock_http_client)

        client_data = CreateClientRequest(
            name="John Doe",
            email="john@example.com",
            phone="+1234567890",
            date_of_birth="1990-01-01",
            gender="male",
            address=Address(
                street="123 Main St",
                city="New York",
                state="NY",
                zip_code="10001"
            )
        )

        client = await clients_api.create_client(client_data)

        assert isinstance(client, Client)
        assert client.name == "John Doe"
        mock_http_client.post.assert_called_once_with("/clients", client_data)

    @pytest.mark.asyncio
    async def test_update_client(self, mock_http_client, sample_client_data):
        """Test updating a client."""
        updated_data = {**sample_client_data, "phone": "+1987654321"}
        mock_http_client.put.return_value = updated_data
        clients_api = ClientsAPI(mock_http_client)

        update_data = UpdateClientRequest(phone="+1987654321")
        client = await clients_api.update_client("client-123", update_data)

        assert isinstance(client, Client)
        assert client.phone == "+1987654321"
        mock_http_client.put.assert_called_once_with("/clients/client-123", update_data)

    @pytest.mark.asyncio
    async def test_delete_client(self, mock_http_client):
        """Test deleting a client."""
        mock_http_client.delete.return_value = {"message": "Client deleted successfully"}
        clients_api = ClientsAPI(mock_http_client)

        response = await clients_api.delete_client("client-123")

        assert isinstance(response, MessageResponse)
        assert "deleted successfully" in response.message
        mock_http_client.delete.assert_called_once_with("/clients/client-123")

    @pytest.mark.asyncio
    async def test_get_client_stats(self, mock_http_client):
        """Test getting client statistics."""
        stats_data = {
            "total_sessions": 10,
            "completed_exercises": 25,
            "average_score": 85.5,
            "last_session_date": "2024-01-15T10:30:00Z",
            "progress_percentage": 75.0
        }
        mock_http_client.get.return_value = stats_data
        clients_api = ClientsAPI(mock_http_client)

        stats = await clients_api.get_client_stats("client-123")

        assert isinstance(stats, ClientStats)
        assert stats.total_sessions == 10
        assert stats.completed_exercises == 25
        assert stats.average_score == 85.5
        mock_http_client.get.assert_called_once_with("/clients/client-123/stats")

    @pytest.mark.asyncio
    async def test_get_client_programs(self, mock_http_client, sample_program_data, sample_paginated_response):
        """Test getting client programs."""
        mock_http_client.get.return_value = sample_paginated_response([sample_program_data])
        clients_api = ClientsAPI(mock_http_client)

        response = await clients_api.get_client_programs(
            "client-123",
            page=1,
            limit=10,
            search="rehab"
        )

        assert isinstance(response, ProgramsListResponse)
        assert len(response.data) == 1
        assert response.data[0].name == "Test Program"

        mock_http_client.get.assert_called_once_with(
            "/clients/client-123/programs",
            {"page": 1, "limit": 10, "search": "rehab"}
        )

    @pytest.mark.asyncio
    async def test_assign_program_to_client(self, mock_http_client):
        """Test assigning a program to a client."""
        mock_http_client.post.return_value = {"success": True}
        clients_api = ClientsAPI(mock_http_client)

        response = await clients_api.assign_program_to_client(
            client_id="client-123",
            program_id="program-456",
            start_date="2024-01-01",
            end_date="2024-04-01",
            notes="Rehabilitation program"
        )

        assert isinstance(response, SuccessResponse)
        assert response.success is True

        mock_http_client.post.assert_called_once_with(
            "/clients/client-123/programs/program-456",
            {
                "start_date": "2024-01-01",
                "end_date": "2024-04-01",
                "notes": "Rehabilitation program"
            }
        )

    @pytest.mark.asyncio
    async def test_assign_program_minimal(self, mock_http_client):
        """Test assigning a program with minimal data."""
        mock_http_client.post.return_value = {"success": True}
        clients_api = ClientsAPI(mock_http_client)

        response = await clients_api.assign_program_to_client(
            client_id="client-123",
            program_id="program-456"
        )

        assert isinstance(response, SuccessResponse)
        mock_http_client.post.assert_called_once_with(
            "/clients/client-123/programs/program-456",
            {}
        )

    @pytest.mark.asyncio
    async def test_remove_client_program(self, mock_http_client):
        """Test removing a program from a client."""
        mock_http_client.delete.return_value = {"message": "Program assignment removed"}
        clients_api = ClientsAPI(mock_http_client)

        response = await clients_api.remove_client_program("client-123", "program-456")

        assert isinstance(response, MessageResponse)
        assert "removed" in response.message
        mock_http_client.delete.assert_called_once_with("/clients/client-123/programs/program-456")

    @pytest.mark.asyncio
    async def test_client_not_found(self, mock_http_client):
        """Test handling client not found error."""
        mock_http_client.get.side_effect = NotFoundError(
            "Client not found",
            status_code=404
        )
        clients_api = ClientsAPI(mock_http_client)

        with pytest.raises(NotFoundError) as exc_info:
            await clients_api.get_client("non-existent")

        assert exc_info.value.status_code == 404

    @pytest.mark.asyncio
    async def test_create_client_validation_error(self, mock_http_client):
        """Test validation error when creating client."""
        mock_http_client.post.side_effect = ValidationError(
            "Invalid client data",
            status_code=422,
            response_data={"errors": {"email": ["Invalid email format"]}}
        )
        clients_api = ClientsAPI(mock_http_client)

        client_data = CreateClientRequest(
            name="John Doe",
            email="invalid-email"
        )

        with pytest.raises(ValidationError) as exc_info:
            await clients_api.create_client(client_data)

        assert exc_info.value.status_code == 422
        assert "email" in exc_info.value.response_data["errors"]