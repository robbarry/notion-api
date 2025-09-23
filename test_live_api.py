#!/usr/bin/env python
"""Test script to verify the Notion API client works with real API."""

from notion_api import NotionClient

def test_real_api():
    """Test the client with actual Notion API."""
    try:
        # Initialize client (will use NOTION_TOKEN from .env)
        client = NotionClient()
        print("✅ Client initialized successfully")

        # Try to list databases
        print("\n📚 Attempting to list databases...")
        databases = client.list_databases(page_size=10)

        if databases:
            print(f"✅ Found {len(databases)} database(s)")
            for db in databases[:3]:  # Show first 3
                db_name = db.get('title', [{}])[0].get('text', {}).get('content', 'Untitled')
                print(f"   - {db_name} (ID: {db['id'][:8]}...)")
        else:
            print("⚠️  No databases found (this is OK if the integration has no access yet)")

        return True

    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    success = test_real_api()
    exit(0 if success else 1)