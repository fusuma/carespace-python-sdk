"""
Main Carespace API client.
"""

from typing import Optional, Any
import warnings

from .http_client import HTTPClient
from .api import AuthAPI, UsersAPI, ClientsAPI, ProgramsAPI
from .models import LoginResponse


class CarespaceClient:
    """
    Main client for interacting with the Carespace API.
    
    This client provides access to all Carespace API endpoints through
    organized sub-clients for different resource types.
    
    Example:
        ```python
        import asyncio
        from carespace_sdk import CarespaceClient
        
        async def main():
            async with CarespaceClient(api_key="your-api-key") as client:
                # Authenticate
                login_response = await client.auth.login("user@example.com", "password")
                client.set_api_key(login_response.access_token)
                
                # Get users
                users = await client.users.get_users(page=1, limit=10)
                print(f"Found {len(users.data)} users")
                
                # Create a client
                from carespace_sdk import CreateClientRequest
                client_data = CreateClientRequest(name="John Doe", email="john@example.com")
                new_client = await client.clients.create_client(client_data)
                print(f"Created client: {new_client.id}")
        
        asyncio.run(main())
        ```
    """

    def __init__(
        self,
        base_url: str = "https://api-dev.carespace.ai",
        api_key: Optional[str] = None,
        timeout: float = 30.0,
        max_retries: int = 3,
        **kwargs: Any,
    ) -> None:
        """
        Initialize the Carespace client.

        Args:
            base_url: Base URL for the Carespace API. Defaults to development environment.
            api_key: API key for authentication. Can be set later using set_api_key().
            timeout: Request timeout in seconds.
            max_retries: Maximum number of retries for failed requests.
            **kwargs: Additional arguments passed to the HTTP client.
            
        Note:
            For production use, set base_url to "https://api.carespace.ai"
        """
        self._http_client = HTTPClient(
            base_url=base_url,
            api_key=api_key,
            timeout=timeout,
            max_retries=max_retries,
            **kwargs,
        )

        # Initialize API endpoints
        self.auth = AuthAPI(self._http_client)
        self.users = UsersAPI(self._http_client)
        self.clients = ClientsAPI(self._http_client)
        self.programs = ProgramsAPI(self._http_client)

    async def __aenter__(self) -> "CarespaceClient":
        """Async context manager entry."""
        return self

    async def __aexit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        """Async context manager exit."""
        await self.close()

    async def close(self) -> None:
        """Close the client and cleanup resources."""
        await self._http_client.close()

    def set_api_key(self, api_key: str) -> None:
        """
        Set or update the API key for authentication.

        Args:
            api_key: The API key to use for authentication.
            
        Note:
            This will update the Authorization header for all subsequent requests.
        """
        self._http_client.set_api_key(api_key)

    @property
    def base_url(self) -> str:
        """Get the current base URL."""
        return self._http_client.base_url

    @property
    def api_key(self) -> Optional[str]:
        """Get the current API key (if set)."""
        return self._http_client.api_key

    async def login_and_set_token(self, email: str, password: str) -> LoginResponse:
        """
        Convenience method to login and automatically set the access token.

        Args:
            email: User email address
            password: User password

        Returns:
            LoginResponse: Authentication response with tokens
            
        Note:
            This method automatically calls set_api_key() with the received access token.
        """
        login_response = await self.auth.login(email, password)
        self.set_api_key(login_response.access_token)
        return login_response

    # Convenience methods for quick access to common operations

    async def quick_get_users(self, limit: int = 20, search: Optional[str] = None):
        """
        Quick method to get users with minimal parameters.
        
        Args:
            limit: Number of users to retrieve (max 100)
            search: Optional search query
            
        Returns:
            UsersListResponse: List of users
        """
        return await self.users.get_users(limit=limit, search=search)

    async def quick_get_clients(self, limit: int = 20, search: Optional[str] = None):
        """
        Quick method to get clients with minimal parameters.
        
        Args:
            limit: Number of clients to retrieve (max 100)
            search: Optional search query
            
        Returns:
            ClientsListResponse: List of clients
        """
        return await self.clients.get_clients(limit=limit, search=search)

    async def quick_get_programs(self, limit: int = 20, category: Optional[str] = None):
        """
        Quick method to get programs with minimal parameters.
        
        Args:
            limit: Number of programs to retrieve (max 100)
            category: Optional category filter
            
        Returns:
            ProgramsListResponse: List of programs
        """
        return await self.programs.get_programs(limit=limit, category=category)

    # Health check and utility methods

    async def health_check(self) -> bool:
        """
        Perform a simple health check to verify API connectivity.
        
        Returns:
            bool: True if the API is reachable and responding
        """
        try:
            # Try to get user profile (requires authentication)
            if self.api_key:
                await self.users.get_user_profile()
                return True
            else:
                # If no API key, just check if we can reach the API
                # This would typically be a /health endpoint, but we'll use users for now
                await self.users.get_users(limit=1)
                return True
        except Exception:
            return False


# Backward compatibility and convenience
CarespaceAPI = CarespaceClient  # Alias for backward compatibility


def create_client(
    base_url: str = "https://api-dev.carespace.ai",
    api_key: Optional[str] = None,
    **kwargs: Any,
) -> CarespaceClient:
    """
    Factory function to create a Carespace client.
    
    Args:
        base_url: Base URL for the API
        api_key: API key for authentication
        **kwargs: Additional arguments passed to CarespaceClient
        
    Returns:
        CarespaceClient: Configured client instance
    """
    return CarespaceClient(base_url=base_url, api_key=api_key, **kwargs)


def create_production_client(api_key: str, **kwargs: Any) -> CarespaceClient:
    """
    Factory function to create a client configured for production.
    
    Args:
        api_key: API key for authentication
        **kwargs: Additional arguments passed to CarespaceClient
        
    Returns:
        CarespaceClient: Client configured for production environment
    """
    return CarespaceClient(
        base_url="https://api.carespace.ai",
        api_key=api_key,
        **kwargs,
    )


def create_development_client(api_key: Optional[str] = None, **kwargs: Any) -> CarespaceClient:
    """
    Factory function to create a client configured for development.
    
    Args:
        api_key: API key for authentication (optional for development)
        **kwargs: Additional arguments passed to CarespaceClient
        
    Returns:
        CarespaceClient: Client configured for development environment
    """
    return CarespaceClient(
        base_url="https://api-dev.carespace.ai",
        api_key=api_key,
        **kwargs,
    )