"""
Tests for the HTTP client.
"""

import pytest
import httpx
from unittest.mock import AsyncMock, patch, MagicMock

from carespace_sdk.http_client import HTTPClient
from carespace_sdk.exceptions import (
    AuthenticationError,
    ValidationError,
    NotFoundError,
    ServerError,
    NetworkError,
    RateLimitError,
    TimeoutError,
    CarespaceError,
)


class TestHTTPClient:
    """Test the HTTP client."""

    def test_initialization(self):
        """Test HTTP client initialization."""
        client = HTTPClient(
            base_url="https://api.example.com",
            api_key="test-key",
            timeout=60.0,
            max_retries=5
        )
        
        assert client.base_url == "https://api.example.com"
        assert client.api_key == "test-key"
        assert client.timeout == 60.0
        assert client.max_retries == 5

    def test_set_api_key(self):
        """Test setting API key."""
        client = HTTPClient()
        client.set_api_key("new-key")
        assert client.api_key == "new-key"

    @pytest.mark.asyncio
    async def test_close(self):
        """Test closing the client."""
        with patch('httpx.AsyncClient') as mock_client_class:
            mock_client = AsyncMock()
            mock_client_class.return_value = mock_client
            
            client = HTTPClient()
            await client.close()
            
            mock_client.aclose.assert_called_once()

    @pytest.mark.asyncio
    async def test_successful_get_request(self):
        """Test successful GET request."""
        with patch('httpx.AsyncClient') as mock_client_class:
            mock_client = AsyncMock()
            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_response.json.return_value = {"data": "test"}
            mock_response.raise_for_status = MagicMock()
            mock_client.get.return_value = mock_response
            mock_client_class.return_value = mock_client
            
            client = HTTPClient(api_key="test-key")
            result = await client.get("/test", {"param": "value"})
            
            assert result == {"data": "test"}
            mock_client.get.assert_called_once_with(
                "/test",
                params={"param": "value"},
                headers={"Authorization": "Bearer test-key"}
            )

    @pytest.mark.asyncio
    async def test_successful_post_request(self):
        """Test successful POST request."""
        with patch('httpx.AsyncClient') as mock_client_class:
            mock_client = AsyncMock()
            mock_response = MagicMock()
            mock_response.status_code = 201
            mock_response.json.return_value = {"id": "123"}
            mock_response.raise_for_status = MagicMock()
            mock_client.post.return_value = mock_response
            mock_client_class.return_value = mock_client
            
            client = HTTPClient(api_key="test-key")
            result = await client.post("/test", {"name": "test"})
            
            assert result == {"id": "123"}
            mock_client.post.assert_called_once_with(
                "/test",
                json={"name": "test"},
                headers={"Authorization": "Bearer test-key"}
            )

    @pytest.mark.asyncio
    async def test_authentication_error(self):
        """Test authentication error handling."""
        with patch('httpx.AsyncClient') as mock_client_class:
            mock_client = AsyncMock()
            mock_response = MagicMock()
            mock_response.status_code = 401
            mock_response.json.return_value = {"error": "Unauthorized"}
            mock_response.raise_for_status.side_effect = httpx.HTTPStatusError(
                "401 Unauthorized",
                request=MagicMock(),
                response=mock_response
            )
            mock_client.get.return_value = mock_response
            mock_client_class.return_value = mock_client
            
            client = HTTPClient()
            
            with pytest.raises(AuthenticationError) as exc_info:
                await client.get("/test")
            
            assert exc_info.value.status_code == 401
            assert "Unauthorized" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_validation_error(self):
        """Test validation error handling."""
        with patch('httpx.AsyncClient') as mock_client_class:
            mock_client = AsyncMock()
            mock_response = MagicMock()
            mock_response.status_code = 422
            mock_response.json.return_value = {
                "error": "Validation failed",
                "errors": {"email": ["Invalid email"]}
            }
            mock_response.raise_for_status.side_effect = httpx.HTTPStatusError(
                "422 Unprocessable Entity",
                request=MagicMock(),
                response=mock_response
            )
            mock_client.post.return_value = mock_response
            mock_client_class.return_value = mock_client
            
            client = HTTPClient()
            
            with pytest.raises(ValidationError) as exc_info:
                await client.post("/test", {"email": "invalid"})
            
            assert exc_info.value.status_code == 422
            assert "Validation failed" in str(exc_info.value)
            assert "email" in exc_info.value.response_data["errors"]

    @pytest.mark.asyncio
    async def test_not_found_error(self):
        """Test not found error handling."""
        with patch('httpx.AsyncClient') as mock_client_class:
            mock_client = AsyncMock()
            mock_response = MagicMock()
            mock_response.status_code = 404
            mock_response.json.return_value = {"error": "Not found"}
            mock_response.raise_for_status.side_effect = httpx.HTTPStatusError(
                "404 Not Found",
                request=MagicMock(),
                response=mock_response
            )
            mock_client.get.return_value = mock_response
            mock_client_class.return_value = mock_client
            
            client = HTTPClient()
            
            with pytest.raises(NotFoundError) as exc_info:
                await client.get("/test/123")
            
            assert exc_info.value.status_code == 404

    @pytest.mark.asyncio
    async def test_rate_limit_error(self):
        """Test rate limit error handling."""
        with patch('httpx.AsyncClient') as mock_client_class:
            mock_client = AsyncMock()
            mock_response = MagicMock()
            mock_response.status_code = 429
            mock_response.headers = {"Retry-After": "60"}
            mock_response.json.return_value = {"error": "Rate limit exceeded"}
            mock_response.raise_for_status.side_effect = httpx.HTTPStatusError(
                "429 Too Many Requests",
                request=MagicMock(),
                response=mock_response
            )
            mock_client.get.return_value = mock_response
            mock_client_class.return_value = mock_client
            
            client = HTTPClient()
            
            with pytest.raises(RateLimitError) as exc_info:
                await client.get("/test")
            
            assert exc_info.value.status_code == 429
            assert exc_info.value.retry_after == 60

    @pytest.mark.asyncio
    async def test_server_error(self):
        """Test server error handling."""
        with patch('httpx.AsyncClient') as mock_client_class:
            mock_client = AsyncMock()
            mock_response = MagicMock()
            mock_response.status_code = 500
            mock_response.json.return_value = {"error": "Internal server error"}
            mock_response.raise_for_status.side_effect = httpx.HTTPStatusError(
                "500 Internal Server Error",
                request=MagicMock(),
                response=mock_response
            )
            mock_client.get.return_value = mock_response
            mock_client_class.return_value = mock_client
            
            client = HTTPClient()
            
            with pytest.raises(ServerError) as exc_info:
                await client.get("/test")
            
            assert exc_info.value.status_code == 500

    @pytest.mark.asyncio
    async def test_timeout_error(self):
        """Test timeout error handling."""
        with patch('httpx.AsyncClient') as mock_client_class:
            mock_client = AsyncMock()
            mock_client.get.side_effect = httpx.TimeoutException("Request timed out")
            mock_client_class.return_value = mock_client
            
            client = HTTPClient(timeout=30.0)
            
            with pytest.raises(TimeoutError) as exc_info:
                await client.get("/test")
            
            assert exc_info.value.timeout_duration == 30.0
            assert "Request timed out" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_network_error(self):
        """Test network error handling."""
        with patch('httpx.AsyncClient') as mock_client_class:
            mock_client = AsyncMock()
            mock_client.get.side_effect = httpx.ConnectError("Connection failed")
            mock_client_class.return_value = mock_client
            
            client = HTTPClient()
            
            with pytest.raises(NetworkError) as exc_info:
                await client.get("/test")
            
            assert "Connection failed" in str(exc_info.value)
            assert isinstance(exc_info.value.original_exception, httpx.ConnectError)

    @pytest.mark.asyncio
    async def test_pydantic_model_serialization(self):
        """Test sending Pydantic models in requests."""
        from carespace_sdk.models import CreateUserRequest
        
        with patch('httpx.AsyncClient') as mock_client_class:
            mock_client = AsyncMock()
            mock_response = MagicMock()
            mock_response.status_code = 201
            mock_response.json.return_value = {"id": "user-123"}
            mock_response.raise_for_status = MagicMock()
            mock_client.post.return_value = mock_response
            mock_client_class.return_value = mock_client
            
            client = HTTPClient()
            user_data = CreateUserRequest(
                email="test@example.com",
                name="Test User"
            )
            
            result = await client.post("/users", user_data)
            
            assert result == {"id": "user-123"}
            # Verify that the Pydantic model was serialized to dict
            call_args = mock_client.post.call_args
            json_data = call_args[1]["json"]
            assert json_data["email"] == "test@example.com"
            assert json_data["name"] == "Test User"

    @pytest.mark.asyncio
    async def test_retry_logic(self):
        """Test retry logic for transient errors."""
        with patch('httpx.AsyncClient') as mock_client_class:
            mock_client = AsyncMock()
            
            # First call fails with network error, second succeeds
            network_error = httpx.ConnectError("Connection failed")
            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_response.json.return_value = {"data": "success"}
            mock_response.raise_for_status = MagicMock()
            
            mock_client.get.side_effect = [network_error, mock_response]
            mock_client_class.return_value = mock_client
            
            client = HTTPClient(max_retries=2)
            
            # Should succeed after retry
            result = await client.get("/test")
            assert result == {"data": "success"}
            assert mock_client.get.call_count == 2

    @pytest.mark.asyncio
    async def test_headers_without_api_key(self):
        """Test request headers when no API key is set."""
        with patch('httpx.AsyncClient') as mock_client_class:
            mock_client = AsyncMock()
            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_response.json.return_value = {"data": "test"}
            mock_response.raise_for_status = MagicMock()
            mock_client.get.return_value = mock_response
            mock_client_class.return_value = mock_client
            
            client = HTTPClient()  # No API key
            await client.get("/test")
            
            # Should not include Authorization header
            call_args = mock_client.get.call_args
            headers = call_args[1].get("headers", {})
            assert "Authorization" not in headers