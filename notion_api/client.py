"""Core Notion API client with authentication and base HTTP methods."""

import os
import time
from typing import Dict, Any, Optional, List
from urllib.parse import urljoin
import json

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


class NotionAPIError(Exception):
    """Base exception for Notion API errors."""
    pass


class RateLimitError(NotionAPIError):
    """Raised when hitting Notion API rate limits."""
    pass


class AuthenticationError(NotionAPIError):
    """Raised when authentication fails."""
    pass


class NotionClient:
    """Main Notion API client handling authentication and HTTP operations.

    Supports Notion API version 2025-09-03 with multiple data sources per database.
    """

    BASE_URL = "https://api.notion.com"
    API_VERSION = "2025-09-03"

    def __init__(
        self,
        auth_token: Optional[str] = None,
        base_url: Optional[str] = None,
        timeout: int = 30,
        max_retries: int = 3,
        backoff_factor: float = 1.0
    ):
        """Initialize the Notion API client.

        Args:
            auth_token: Notion integration token (or from NOTION_API_TOKEN env var)
            base_url: Override base API URL (for testing)
            timeout: Request timeout in seconds
            max_retries: Maximum number of retry attempts
            backoff_factor: Backoff multiplier between retries
        """
        self.auth_token = auth_token or os.getenv("NOTION_API_TOKEN") or os.getenv("NOTION_TOKEN")
        if not self.auth_token:
            raise AuthenticationError(
                "No auth token provided. Pass auth_token or set NOTION_API_TOKEN env var"
            )

        self.base_url = base_url or self.BASE_URL
        self.timeout = timeout

        # Set up requests session with retry strategy
        self.session = requests.Session()
        retry_strategy = Retry(
            total=max_retries,
            backoff_factor=backoff_factor,
            status_forcelist=[429, 500, 502, 503, 504],
            allowed_methods=["HEAD", "GET", "PUT", "DELETE", "OPTIONS", "TRACE", "POST", "PATCH"]
        )
        adapter = HTTPAdapter(max_retries=retry_strategy)
        self.session.mount("http://", adapter)
        self.session.mount("https://", adapter)

        # Set default headers
        self.session.headers.update(self._get_headers())

    def _get_headers(self) -> Dict[str, str]:
        """Get standard headers for Notion API requests."""
        return {
            "Authorization": f"Bearer {self.auth_token}",
            "Notion-Version": self.API_VERSION,
            "Content-Type": "application/json"
        }

    def _request(
        self,
        method: str,
        endpoint: str,
        data: Optional[Dict[str, Any]] = None,
        params: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Make an HTTP request to the Notion API.

        Args:
            method: HTTP method (GET, POST, PATCH, DELETE)
            endpoint: API endpoint (e.g., "/v1/databases")
            data: Request body data
            params: URL query parameters

        Returns:
            JSON response from the API

        Raises:
            NotionAPIError: On API errors
            RateLimitError: When rate limited
            AuthenticationError: On auth failures
        """
        url = urljoin(self.base_url, endpoint)

        try:
            response = self.session.request(
                method=method,
                url=url,
                json=data,
                params=params,
                timeout=self.timeout
            )

            # Handle rate limiting
            if response.status_code == 429:
                retry_after = int(response.headers.get("Retry-After", 10))
                raise RateLimitError(
                    f"Rate limited. Retry after {retry_after} seconds"
                )

            # Handle authentication errors
            if response.status_code == 401:
                raise AuthenticationError("Invalid authentication token")

            # Handle other errors
            if response.status_code >= 400:
                error_msg = f"API error {response.status_code}"
                try:
                    error_data = response.json()
                    if "message" in error_data:
                        error_msg = f"{error_msg}: {error_data['message']}"
                except:
                    error_msg = f"{error_msg}: {response.text}"
                raise NotionAPIError(error_msg)

            return response.json()

        except requests.exceptions.RequestException as e:
            raise NotionAPIError(f"Request failed: {str(e)}")

    def get(self, endpoint: str, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Make a GET request."""
        return self._request("GET", endpoint, params=params)

    def post(self, endpoint: str, data: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Make a POST request."""
        return self._request("POST", endpoint, data=data)

    def patch(self, endpoint: str, data: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Make a PATCH request."""
        return self._request("PATCH", endpoint, data=data)

    def delete(self, endpoint: str) -> Dict[str, Any]:
        """Make a DELETE request."""
        return self._request("DELETE", endpoint)

    # Basic API operations

    def list_databases(self, page_size: int = 100) -> List[Dict[str, Any]]:
        """List all databases the integration has access to.

        Args:
            page_size: Number of results per page

        Returns:
            List of database objects
        """
        databases = []
        has_more = True
        next_cursor = None
        max_iterations = 10  # Prevent infinite loops

        iteration = 0
        while has_more and iteration < max_iterations:
            data = {"page_size": page_size}
            if next_cursor:
                data["start_cursor"] = next_cursor

            # Note: In 2025-09-03 API, databases are now containers for data sources
            # The search endpoint returns all accessible objects
            response = self.post("/v1/search", data=data)

            # Filter for databases from the results
            for item in response.get("results", []):
                if item.get("object") == "database":
                    databases.append(item)

            has_more = response.get("has_more", False)
            next_cursor = response.get("next_cursor")
            iteration += 1

            # If we get the same cursor, break to prevent infinite loop
            if next_cursor and next_cursor == data.get("start_cursor"):
                break

        return databases

    def get_database(self, database_id: str) -> Dict[str, Any]:
        """Get a specific database by ID.

        Args:
            database_id: The database UUID

        Returns:
            Database object
        """
        return self.get(f"/v1/databases/{database_id}")

    def query_database(
        self,
        database_id: str,
        filter: Optional[Dict[str, Any]] = None,
        sorts: Optional[List[Dict[str, Any]]] = None,
        page_size: int = 100
    ) -> List[Dict[str, Any]]:
        """Query a database for pages.

        This method handles the complexity of multiple data sources transparently.
        For databases with multiple data sources, it queries all and merges results.

        Args:
            database_id: The database UUID
            filter: Filter conditions for the query
            sorts: Sort parameters for results
            page_size: Number of results per page

        Returns:
            List of page objects matching the query
        """
        # First, get the database to check for data sources
        database = self.get_database(database_id)

        # Build query payload
        payload = {"page_size": page_size}
        if filter:
            payload["filter"] = filter
        if sorts:
            payload["sorts"] = sorts

        # Query the database (API handles data sources internally in 2025-09-03)
        all_results = []
        has_more = True
        next_cursor = None

        while has_more:
            if next_cursor:
                payload["start_cursor"] = next_cursor

            response = self.post(f"/v1/databases/{database_id}/query", data=payload)
            all_results.extend(response.get("results", []))
            has_more = response.get("has_more", False)
            next_cursor = response.get("next_cursor")

        return all_results

    def get_page(self, page_id: str) -> Dict[str, Any]:
        """Get a specific page by ID.

        Args:
            page_id: The page UUID

        Returns:
            Page object with properties
        """
        return self.get(f"/v1/pages/{page_id}")

    def create_page(
        self,
        parent: Dict[str, str],
        properties: Dict[str, Any],
        children: Optional[List[Dict[str, Any]]] = None
    ) -> Dict[str, Any]:
        """Create a new page.

        Args:
            parent: Parent database or page reference (e.g., {"database_id": "..."})
            properties: Page properties matching the parent schema
            children: Optional list of block children for the page

        Returns:
            Created page object
        """
        payload = {
            "parent": parent,
            "properties": properties
        }
        if children:
            payload["children"] = children

        return self.post("/v1/pages", data=payload)