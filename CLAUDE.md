# AI Assistant Instructions for Notion API Project

## Project Context

This is a unified Notion API integration layer for three applications:
1. **SignalBot2** - Notification/signal management system
2. **Storyboard** - Content/project management tool
3. **DataHQ** - Data management/analytics platform

## Current State

- **Phase**: Core functionality implemented
- **Implementation**:
  - ✅ Basic Notion API client with authentication (Issue #1)
  - ✅ Full support for 2025-09-03 data sources architecture
  - ✅ Database and data source query operations
  - ✅ Page creation with auto-conversion to data_source_id
  - ✅ SignalBot2 requirements documented (Issue #2)
- **Roadmap**: Issues #3-7 pending (Storyboard/DataHQ requirements, unified interface)

## Technical Requirements

### API Version
- **Current Version**: Notion API version 2025-09-03 (as of September 2025)
- **IMPORTANT**: This is the CURRENT version, not a future version!
- **Breaking Change**: Databases are now containers for data sources
- **Key Endpoints Changed**:
  - ❌ `/v1/databases/{id}/query` - NO LONGER EXISTS
  - ✅ `/v1/data_sources/{id}/query` - Use this instead
  - ✅ `/v1/databases/{id}` - Returns database with `data_sources` array
- **Backwards Compatibility**: Must support legacy single-data-source databases

### Architecture Goals
- Single unified interface for all three applications
- Hide complexity of data sources vs databases from apps
- Provide app-specific adapters with helper methods
- Centralized authentication and configuration

## Development Priorities

1. **Issue #1**: Set up basic Notion API client with authentication
2. **Issues #2-4**: Gather requirements from each application
3. **Issue #5**: Implement core database operations (with data sources)
4. **Issue #6**: Implement page and block operations
5. **Issue #7**: Create unified interface layer

## Code Standards

### Python Development
- Use `uv` for package management (`uv add`, `uv run`)
- Python 3.10+ required
- Follow PEP 8 style guidelines
- Type hints for all public methods

### Testing
- Write tests alongside implementation
- Use pytest for testing framework
- Mock Notion API calls for unit tests
- Integration tests with real API (marked appropriately)

### Error Handling
- Graceful handling of rate limits
- Clear error messages for multiple data source scenarios
- Retry logic for transient failures
- Proper logging of API interactions

## Implementation Notes

### Database vs Data Source Architecture (CRITICAL)

⚠️ **Major API Change in 2025-09-03**: Databases are now containers for data sources!

```python
# Old model (pre-2025-09-03):
# database_id directly contains pages
# Query: POST /v1/databases/{database_id}/query

# New model (2025-09-03 - CURRENT):
# database_id → data_source_ids → pages
# Query: POST /v1/data_sources/{data_source_id}/query

# How to migrate:
# 1. GET /v1/databases/{database_id} to get data_sources array
# 2. Use data_source_id from that array for queries
# 3. When creating pages, use {"data_source_id": "..."} parent, not {"database_id": "..."}
```

### Working with Data Sources

```python
# CORRECT way to query a database in 2025-09-03:
database = client.get_database(database_id)
data_sources = database.get('data_sources', [])
if data_sources:
    ds_id = data_sources[0]['id']
    results = client.query_data_source(ds_id, filter={...})

# WRONG - this endpoint doesn't exist anymore:
# results = client.post(f"/v1/databases/{database_id}/query")  # ❌ Returns 400
```

### Key API Endpoints
- `/v1/databases/{id}` - Get database metadata (returns data_sources array)
- `/v1/data_sources/{id}` - Get data source metadata
- `/v1/data_sources/{id}/query` - Query pages in a data source (NOT /v1/databases/{id}/query!)
- `/v1/pages/*` - Page operations
- `/v1/blocks/*` - Block operations

### Authentication
```python
# Headers required for all requests
headers = {
    "Authorization": f"Bearer {token}",
    "Notion-Version": "2025-09-03",
    "Content-Type": "application/json"
}
```

## Common Tasks

### Adding a new feature
1. Create/update relevant GitHub issue
2. Create feature branch from main
3. Implement with tests
4. Update documentation
5. Create PR for review

### Testing changes
```bash
# Run all tests
uv run pytest

# Run specific test file
uv run pytest tests/test_database.py

# Run with coverage
uv run pytest --cov=notion_api
```

### Debugging API calls
- Log all API requests/responses during development
- Check for `multiple_data_sources_for_database` errors
- Verify API version header is set correctly

## Project Structure

```
notion-api/
├── notion_api/           # Main package
│   ├── __init__.py
│   ├── client.py        # Core NotionClient
│   ├── database.py      # Database operations
│   ├── page.py          # Page operations
│   ├── block.py         # Block operations
│   └── adapters/        # App-specific adapters
│       ├── signalbot2.py
│       ├── storyboard.py
│       └── datahq.py
├── tests/               # Test suite
├── docs/                # Documentation
└── examples/            # Usage examples
```

## Resources

- [Notion API Docs](https://developers.notion.com/)
- [2025-09-03 Upgrade Guide](docs/notion-api-upgrading-docs-20250903.txt)
- [GitHub Issues](https://github.com/robbarry/notion-api/issues)

## Notes for AI Assistants

1. **API Version 2025-09-03 is CURRENT** - This is the live version as of September 2025, not a future version!
2. **NEVER use `/v1/databases/{id}/query`** - This endpoint was removed in 2025-09-03. Use `/v1/data_sources/{id}/query` instead
3. **Data sources are MANDATORY** - Every database operation must go through data sources now
4. **Test with real API** - Don't assume old patterns work. The API has breaking changes
5. **Check the data_sources array** - When you GET a database, always check its data_sources before querying
6. **Document decisions** - Use `clog` to document important decisions and findings
7. **Verify with documentation** - When in doubt, check [Notion API Docs](https://developers.notion.com/)

## Quick Commands

```bash
# Install dependencies
uv sync

# Run the main script
uv run python main.py

# Run tests
uv run pytest

# Check code style
uv run ruff check .

# Format code
uv run ruff format .
```