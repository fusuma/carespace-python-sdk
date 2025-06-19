"""
HTTP client for making API requests to the Carespace API.
"""

import asyncio
from typing import Any, Dict, Optional, Union
from urllib.parse import urljoin, urlencode

import httpx
from pydantic import BaseModel

from .exceptions import (
    CarespaceError,
    AuthenticationError,
    ValidationError,
    NotFoundError,
    ServerError,
    NetworkError,
    RateLimitError,
    TimeoutError,
)


class HTTPClient:
    """Async HTTP client for Carespace API requests."""

    def __init__(
        self,
        base_url: str = "https://api-dev.carespace.ai",
        api_key: Optional[str] = None,
        timeout: float = 30.0,
        max_retries: int = 3,
        **kwargs: Any,
    ) -> None:
        """
        Initialize the HTTP client.

        Args:
            base_url: Base URL for the API
            api_key: API key for authentication
            timeout: Request timeout in seconds
            max_retries: Maximum number of retries for failed requests
            **kwargs: Additional arguments passed to httpx.AsyncClient
        """
        self.base_url = base_url.rstrip("/")
        self.api_key = api_key
        self.timeout = timeout
        self.max_retries = max_retries

        # Default headers
        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json",
            "User-Agent": "carespace-python-sdk/1.0.0",
        }
        
        if api_key:
            headers["Authorization"] = f"Bearer {api_key}"

        # Merge with any provided headers
        if "headers" in kwargs:
            headers.update(kwargs.pop("headers"))

        self._client = httpx.AsyncClient(
            base_url=self.base_url,
            headers=headers,
            timeout=httpx.Timeout(timeout),
            **kwargs,
        )

    async def __aenter__(self) -> "HTTPClient":
        """Async context manager entry."""
        return self

    async def __aexit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        """Async context manager exit."""
        await self.close()

    async def close(self) -> None:
        """Close the HTTP client."""
        await self._client.aclose()

    def set_api_key(self, api_key: str) -> None:
        """Update the API key for authentication."""
        self.api_key = api_key
        self._client.headers["Authorization"] = f"Bearer {api_key}"

    def _build_url(self, endpoint: str, params: Optional[Dict[str, Any]] = None) -> str:
        """Build the full URL for an API endpoint."""
        url = urljoin(self.base_url, endpoint.lstrip("/"))
        
        if params:
            # Filter out None values and convert to strings
            clean_params = {
                k: str(v) for k, v in params.items() 
                if v is not None and v != ""
            }
            if clean_params:
                url += "?" + urlencode(clean_params)
        
        return url

    def _handle_response_error(self, response: httpx.Response) -> None:
        """Handle HTTP response errors and raise appropriate exceptions."""
        try:
            error_data = response.json()
            error_message = error_data.get("message", error_data.get("error", response.text))
        except Exception:
            error_message = response.text or f"HTTP {response.status_code}"

        if response.status_code == 401:
            raise AuthenticationError(error_message, response.status_code, error_data)
        elif response.status_code == 400:
            raise ValidationError(error_message, response.status_code, error_data)
        elif response.status_code == 404:
            raise NotFoundError(error_message, response.status_code, error_data)
        elif response.status_code == 429:
            retry_after = response.headers.get("Retry-After")
            raise RateLimitError(
                error_message,
                response.status_code,
                int(retry_after) if retry_after else None,
                error_data,
            )
        elif 400 <= response.status_code < 500:
            raise ValidationError(error_message, response.status_code, error_data)
        elif response.status_code >= 500:
            raise ServerError(error_message, response.status_code, error_data)
        else:
            raise CarespaceError(error_message, response.status_code, error_data)

    async def _request_with_retry(
        self,
        method: str,
        endpoint: str,
        json_data: Optional[Union[Dict[str, Any], BaseModel]] = None,
        params: Optional[Dict[str, Any]] = None,
        **kwargs: Any,
    ) -> Dict[str, Any]:
        """Make an HTTP request with retry logic."""
        url = self._build_url(endpoint, params)
        
        # Convert Pydantic model to dict if needed
        if isinstance(json_data, BaseModel):
            json_data = json_data.model_dump(exclude_none=True)

        last_exception = None
        
        for attempt in range(self.max_retries + 1):
            try:
                response = await self._client.request(
                    method=method,
                    url=url,
                    json=json_data,
                    **kwargs,
                )
                
                # Check for HTTP errors
                if not response.is_success:
                    self._handle_response_error(response)
                
                # Parse JSON response
                try:
                    return response.json()
                except Exception:
                    # If response is not JSON, return empty dict
                    return {}
                    
            except httpx.TimeoutException as e:
                last_exception = TimeoutError(f"Request timed out after {self.timeout}s", self.timeout)
                if attempt == self.max_retries:
                    raise last_exception
                    
            except httpx.NetworkError as e:
                last_exception = NetworkError(f"Network error: {e}", e)
                if attempt == self.max_retries:
                    raise last_exception
                    
            except (AuthenticationError, ValidationError, NotFoundError) as e:
                # Don't retry client errors
                raise e
                
            except Exception as e:
                last_exception = CarespaceError(f"Unexpected error: {e}")
                if attempt == self.max_retries:
                    raise last_exception
            
            # Exponential backoff for retries
            if attempt < self.max_retries:
                wait_time = 2 ** attempt
                await asyncio.sleep(wait_time)
        
        # This shouldn't be reached, but just in case
        if last_exception:
            raise last_exception
        raise CarespaceError("Request failed after all retries")

    async def get(
        self,
        endpoint: str,
        params: Optional[Dict[str, Any]] = None,
        **kwargs: Any,
    ) -> Dict[str, Any]:
        """Make a GET request."""
        return await self._request_with_retry("GET", endpoint, params=params, **kwargs)

    async def post(
        self,
        endpoint: str,
        json_data: Optional[Union[Dict[str, Any], BaseModel]] = None,
        params: Optional[Dict[str, Any]] = None,
        **kwargs: Any,
    ) -> Dict[str, Any]:
        """Make a POST request."""
        return await self._request_with_retry("POST", endpoint, json_data, params, **kwargs)

    async def put(
        self,
        endpoint: str,
        json_data: Optional[Union[Dict[str, Any], BaseModel]] = None,
        params: Optional[Dict[str, Any]] = None,
        **kwargs: Any,
    ) -> Dict[str, Any]:
        """Make a PUT request."""
        return await self._request_with_retry("PUT", endpoint, json_data, params, **kwargs)

    async def patch(
        self,
        endpoint: str,
        json_data: Optional[Union[Dict[str, Any], BaseModel]] = None,
        params: Optional[Dict[str, Any]] = None,
        **kwargs: Any,
    ) -> Dict[str, Any]:
        """Make a PATCH request."""
        return await self._request_with_retry("PATCH", endpoint, json_data, params, **kwargs)

    async def delete(
        self,
        endpoint: str,
        params: Optional[Dict[str, Any]] = None,
        **kwargs: Any,
    ) -> Dict[str, Any]:
        """Make a DELETE request."""
        return await self._request_with_retry("DELETE", endpoint, params=params, **kwargs)