# AI Assistant Instructions for Notion API Project

## Project Context

This is a unified Notion API integration layer for three applications:
1. **SignalBot2** - Notification/signal management system
2. **Storyboard** - Content/project management tool
3. **DataHQ** - Data management/analytics platform

## Current State

- **Phase**: Initial development (scaffolding only)
- **Implementation**: No functional code yet, just project structure
- **Roadmap**: Defined in GitHub issues #1-7

## Technical Requirements

### API Version
- **Target**: Notion API version 2025-09-03
- **Key Change**: Multiple data sources per database (database is now a container)
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

### Database vs Data Source
```python
# Old model (pre-2025-09-03):
# database_id directly contains pages

# New model (2025-09-03+):
# database_id → data_source_ids → pages
# Must handle both transparently
```

### Key API Endpoints
- `/v1/databases/*` - Database container operations
- `/v1/data_sources/*` - Data source operations (NEW)
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

1. **Always check the current API version** - We're using 2025-09-03, not older versions
2. **Data sources are critical** - Don't ignore the new data source architecture
3. **Test with both models** - Ensure code works with single and multiple data sources
4. **Document decisions** - Use `clog` to document important decisions and findings
5. **Check existing code** - Before implementing, check if similar functionality exists

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