#!/usr/bin/env python
"""Test script to verify the Notion API client works with real API."""

import pytest
from notion_api import NotionClient

def test_real_api():
    """Test the client with actual Notion API."""
    # Initialize client (will use NOTION_TOKEN from .env)
    client = NotionClient()
    print("✅ Client initialized successfully")

    # Try to list databases
    print("\n📚 Attempting to list databases...")
    databases = client.list_databases(page_size=10)

    if databases:
        print(f"✅ Found {len(databases)} database(s)")
        for db in databases[:3]:  # Show first 3
            title_arr = db.get('title', [])
            db_name = title_arr[0].get('plain_text', 'Untitled') if title_arr else 'Untitled'
            print(f"   - {db_name} (ID: {db['id'][:8]}...)")
    else:
        print("⚠️  No databases found (this is OK if the integration has no access yet)")

    # Assert client was created and API call succeeded (even if no databases)
    assert client is not None
    assert isinstance(databases, list)

if __name__ == "__main__":
    test_real_api()
    print("✅ All checks passed")