# Notion API Integration Layer

A unified Python library providing Notion API integration for multiple applications, supporting the latest 2025-09-03 API version with multiple data sources per database.

## Overview

This project provides a consistent, simplified interface to the Notion API for three primary applications:
- **SignalBot2** - Notification and signal management system
- **Storyboard** - Content and project management tool
- **DataHQ** - Data management and analytics platform

## Key Features

- **Modern API Support**: Full compatibility with Notion's 2025-09-03 API version
- **Multiple Data Sources**: Handles the new database architecture with multiple data sources
- **Unified Interface**: Single API abstraction layer for all applications
- **Backwards Compatible**: Supports legacy single-data-source databases
- **Comprehensive Operations**: Database, page, block, and content management
- **Error Handling**: Robust error handling and retry logic
- **Rate Limiting**: Built-in rate limit management

## Installation

```bash
# Install with uv (recommended)
uv add notion-api

# Or with pip
pip install notion-api
```

## Quick Start

```python
from notion_api import NotionClient

# Initialize client with your integration token
client = NotionClient(auth_token="your-notion-integration-token")

# List all databases
databases = client.list_databases()

# Query a database (automatically handles data sources)
results = client.query_database(
    database_id="your-database-id",
    filter={"property": "Status", "select": {"equals": "Active"}}
)

# Create a new page
page = client.create_page(
    parent_id="parent-page-or-database-id",
    properties={
        "Name": {"title": [{"text": {"content": "New Page"}}]},
        "Status": {"select": {"name": "Active"}}
    }
)
```

## Application-Specific Adapters

### SignalBot2
```python
from notion_api.adapters import SignalBot2Adapter

signal_client = SignalBot2Adapter(auth_token="token")
# SignalBot2-specific operations
```

### Storyboard
```python
from notion_api.adapters import StoryboardAdapter

story_client = StoryboardAdapter(auth_token="token")
# Storyboard-specific operations
```

### DataHQ
```python
from notion_api.adapters import DataHQAdapter

data_client = DataHQAdapter(auth_token="token")
# DataHQ-specific operations
```

## Development Status

See our [GitHub Issues](https://github.com/robbarry/notion-api/issues) for the development roadmap:

- [ ] #1 - Set up basic Notion API client with authentication
- [ ] #2 - Define requirements for SignalBot2 integration
- [ ] #3 - Define requirements for Storyboard integration
- [ ] #4 - Define requirements for DataHQ integration
- [ ] #5 - Implement core database operations
- [ ] #6 - Implement page and block operations
- [ ] #7 - Create unified API interface

## API Version Support

This library supports the Notion API version 2025-09-03, which introduces:
- Multiple data sources per database
- Separate database (container) and data source concepts
- New `/v1/data_sources` endpoints

For backwards compatibility, the library also handles databases with single data sources transparently.

## Configuration

Set your Notion integration token as an environment variable:
```bash
export NOTION_API_TOKEN="your-integration-token"
```

Or pass it directly to the client:
```python
client = NotionClient(auth_token="your-integration-token")
```

## Testing

```bash
# Run tests with pytest
uv run pytest

# Run with coverage
uv run pytest --cov=notion_api
```

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## Documentation

- [Notion API Documentation](https://developers.notion.com/)
- [API Upgrade Guide (2025-09-03)](docs/notion-api-upgrading-docs-20250903.txt)
- [Requirements Matrix](docs/index.md)

## License

This project is proprietary and confidential.

## Support

For issues and questions, please use the [GitHub Issues](https://github.com/robbarry/notion-api/issues) page.