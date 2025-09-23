"""Tests for the NotionClient core functionality."""

import os
import pytest
from unittest.mock import Mock, patch, MagicMock
import requests

from notion_api import NotionClient
from notion_api.client import NotionAPIError, RateLimitError, AuthenticationError


class TestNotionClient:
    """Test suite for NotionClient."""

    def test_init_with_token(self):
        """Test client initialization with explicit token."""
        client = NotionClient(auth_token="test-token-123")
        assert client.auth_token == "test-token-123"
        assert client.base_url == "https://api.notion.com"
        assert client.timeout == 30

    def test_init_with_env_token(self):
        """Test client initialization with environment variable."""
        with patch.dict(os.environ, {"NOTION_API_TOKEN": "env-token-456"}, clear=True):
            client = NotionClient()
            assert client.auth_token == "env-token-456"

    def test_token_precedence(self):
        """Test that NOTION_API_TOKEN takes precedence over NOTION_TOKEN."""
        with patch.dict(os.environ, {
            "NOTION_TOKEN": "notion-token",
            "NOTION_API_TOKEN": "api-token"
        }, clear=True):
            client = NotionClient()
            assert client.auth_token == "api-token"

        # Test fallback to NOTION_TOKEN when NOTION_API_TOKEN is not set
        with patch.dict(os.environ, {"NOTION_TOKEN": "notion-token"}, clear=True):
            client = NotionClient()
            assert client.auth_token == "notion-token"

    def test_init_without_token_raises_error(self):
        """Test that missing token raises AuthenticationError."""
        with patch.dict(os.environ, {}, clear=True):
            with pytest.raises(AuthenticationError, match="No auth token provided"):
                NotionClient()

    def test_headers_include_auth_and_version(self):
        """Test that request headers are properly set."""
        client = NotionClient(auth_token="test-token")
        headers = client._get_headers()

        assert headers["Authorization"] == "Bearer test-token"
        assert headers["Notion-Version"] == "2025-09-03"
        assert headers["Content-Type"] == "application/json"

    @patch('notion_api.client.requests.Session')
    def test_rate_limit_error(self, mock_session_class):
        """Test that 429 responses raise RateLimitError."""
        mock_session = MagicMock()
        mock_session_class.return_value = mock_session

        mock_response = Mock()
        mock_response.status_code = 429
        mock_response.headers = {"Retry-After": "5"}
        mock_session.request.return_value = mock_response

        client = NotionClient(auth_token="test-token")

        with pytest.raises(RateLimitError, match="Rate limited"):
            client.get("/v1/databases")

    @patch('notion_api.client.requests.Session')
    def test_authentication_error(self, mock_session_class):
        """Test that 401 responses raise AuthenticationError."""
        mock_session = MagicMock()
        mock_session_class.return_value = mock_session

        mock_response = Mock()
        mock_response.status_code = 401
        mock_session.request.return_value = mock_response

        client = NotionClient(auth_token="test-token")

        with pytest.raises(AuthenticationError, match="Invalid authentication token"):
            client.get("/v1/databases")

    @patch('notion_api.client.requests.Session')
    def test_generic_api_error(self, mock_session_class):
        """Test that 4xx/5xx responses raise NotionAPIError."""
        mock_session = MagicMock()
        mock_session_class.return_value = mock_session

        mock_response = Mock()
        mock_response.status_code = 400
        mock_response.json.return_value = {"message": "Bad request"}
        mock_session.request.return_value = mock_response

        client = NotionClient(auth_token="test-token")

        with pytest.raises(NotionAPIError, match="Bad request"):
            client.get("/v1/databases")

    @patch('notion_api.client.requests.Session')
    def test_successful_get_request(self, mock_session_class):
        """Test successful GET request."""
        mock_session = MagicMock()
        mock_session_class.return_value = mock_session

        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"object": "database", "id": "123"}
        mock_session.request.return_value = mock_response

        client = NotionClient(auth_token="test-token")
        result = client.get("/v1/databases/123")

        assert result == {"object": "database", "id": "123"}
        mock_session.request.assert_called_once()

    @patch('notion_api.client.requests.Session')
    def test_list_databases_pagination(self, mock_session_class):
        """Test list_databases handles pagination correctly."""
        mock_session = MagicMock()
        mock_session_class.return_value = mock_session

        # First page response
        first_response = Mock()
        first_response.status_code = 200
        first_response.json.return_value = {
            "results": [
                {"id": "db1", "object": "database"},
                {"id": "db2", "object": "database"}
            ],
            "has_more": True,
            "next_cursor": "cursor-123"
        }

        # Second page response
        second_response = Mock()
        second_response.status_code = 200
        second_response.json.return_value = {
            "results": [{"id": "db3", "object": "database"}],
            "has_more": False,
            "next_cursor": None
        }

        mock_session.request.side_effect = [first_response, second_response]

        client = NotionClient(auth_token="test-token")
        databases = client.list_databases()

        assert len(databases) == 3
        assert databases[0]["id"] == "db1"
        assert databases[2]["id"] == "db3"

    @patch('notion_api.client.requests.Session')
    def test_query_database(self, mock_session_class):
        """Test query_database method."""
        mock_session = MagicMock()
        mock_session_class.return_value = mock_session

        # Mock get_database response
        db_response = Mock()
        db_response.status_code = 200
        db_response.json.return_value = {"object": "database", "id": "db-123"}

        # Mock query response
        query_response = Mock()
        query_response.status_code = 200
        query_response.json.return_value = {
            "results": [{"id": "page1"}, {"id": "page2"}],
            "has_more": False
        }

        mock_session.request.side_effect = [db_response, query_response]

        client = NotionClient(auth_token="test-token")
        results = client.query_database(
            "db-123",
            filter={"property": "Status", "select": {"equals": "Active"}}
        )

        assert len(results) == 2
        assert results[0]["id"] == "page1"

    @patch('notion_api.client.requests.Session')
    def test_create_page(self, mock_session_class):
        """Test create_page method."""
        mock_session = MagicMock()
        mock_session_class.return_value = mock_session

        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "object": "page",
            "id": "new-page-123",
            "properties": {"Name": {"title": [{"text": {"content": "Test Page"}}]}}
        }
        mock_session.request.return_value = mock_response

        client = NotionClient(auth_token="test-token")
        page = client.create_page(
            parent={"database_id": "db-123"},
            properties={"Name": {"title": [{"text": {"content": "Test Page"}}]}}
        )

        assert page["id"] == "new-page-123"
        assert page["object"] == "page"