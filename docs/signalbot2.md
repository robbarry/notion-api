# SignalBot2 Requirements

SignalBot2 is a sophisticated notification and signal management system with extensive Notion integration for tracking work activities, managing events, and storing conversation data.

## Core Functional Requirements

### Database Operations

**SB2-R-001** | Database Discovery and Resolution
- List all accessible databases with metadata
- Resolve database names to IDs with caching
- Support dynamic discovery via MCP protocol
- Handle both legacy single-data-source and new multi-data-source databases

**SB2-R-002** | Database Querying
- Query databases with complex filters (compound conditions, date ranges)
- Support sorting by multiple properties
- Handle pagination for large result sets (100+ items)
- Return results with all property values decoded

**SB2-R-003** | Schema Introspection
- Get database schema including all property definitions
- Retrieve property IDs for create/update operations
- Support property type validation before operations

### Page Operations

**SB2-R-004** | Page Creation
- Create pages in any database with full property mapping
- Support rich text formatting in title and content blocks
- Handle timestamps and user references
- Support batch creation for efficiency

**SB2-R-005** | Page Updates
- Update existing pages with partial property changes
- Support atomic updates to prevent race conditions
- Handle version conflicts gracefully
- Preserve unchanged properties

**SB2-R-006** | Page Retrieval
- Get full page content including all blocks
- Support filtered property retrieval
- Handle large pages with block pagination
- Include metadata (created/modified times, users)

### Specialized Operations

**SB2-R-007** | Worklog Management
- Create timestamped worklog entries with user attribution
- Query worklogs by date range and user
- Support activity categorization and tagging
- Handle timezone conversions properly

**SB2-R-008** | Event Scheduling
- Create recurring events with complex patterns (cron-like)
- Update event execution status and next run times
- Query upcoming events within time windows
- Support event categories and priorities

**SB2-R-009** | User Facts Storage
- Store user preferences with expiration dates
- Support fact versioning and history
- Query facts by user, category, or pattern
- Handle fact privacy and access controls

**SB2-R-010** | Conversation Summaries
- Store AI-generated summaries with metadata
- Link summaries to original conversations
- Support summary search and retrieval
- Handle summary versioning and updates

### Search and Discovery

**SB2-R-011** | Cross-Database Search
- Search across multiple databases simultaneously
- Support full-text search in page content
- Filter by properties, dates, and users
- Rank results by relevance

**SB2-R-012** | Semantic Search
- Search conversation history semantically
- Support vector similarity search (if available)
- Handle search result summarization
- Integrate with AI models for enhanced search

### Integration Requirements

**SB2-R-013** | MCP Tool Compatibility
- Maintain compatibility with existing MCP tool names (`mcp__notion__*`)
- Support dynamic tool discovery at startup
- Handle tool parameter validation
- Limit response sizes (100k characters)

**SB2-R-014** | Legacy API Migration
- Support migration from wsjd.at HQ endpoints
- Provide compatibility layer for existing code
- Handle gradual migration without breaking changes
- Document migration path clearly

## Performance Requirements

**SB2-P-001** | Response Time
- Database queries should complete within 2 seconds
- Page creation/updates within 1 second
- Search operations within 3 seconds
- Support request timeouts and cancellation

**SB2-P-002** | Rate Limiting
- Respect Notion API rate limits automatically
- Implement exponential backoff on rate limit errors
- Queue requests when approaching limits
- Provide rate limit status to applications

**SB2-P-003** | Caching
- Cache database schemas for 5 minutes
- Cache database name→ID mappings for 1 hour
- Support cache invalidation on updates
- Provide cache hit/miss metrics

## Data Model Requirements

### Core Databases

1. **Worklog Database**
   - Properties: Timestamp, User, Activity, Category, Duration, Notes
   - Relations: Links to Projects, Tasks

2. **Scheduled Events Database**
   - Properties: Name, Pattern, NextRun, LastRun, Status, Category
   - Relations: Links to Actions, Users

3. **User Facts Database**
   - Properties: User, FactKey, FactValue, Category, ExpiresAt
   - Relations: Links to Users

4. **Summaries Database**
   - Properties: Title, Content, Timestamp, Source, Metadata
   - Relations: Links to Conversations, Users

## Authentication and Security

**SB2-S-001** | Token Management
- Support multiple authentication tokens
- Handle token rotation without downtime
- Provide token validation and health checks
- Log authentication failures appropriately

**SB2-S-002** | Access Control
- Respect Notion workspace permissions
- Handle permission errors gracefully
- Support user-specific data filtering
- Audit data access for compliance

## Error Handling

**SB2-E-001** | Graceful Degradation
- Continue operation when non-critical features fail
- Provide fallback options for failed operations
- Queue failed operations for retry
- Alert on persistent failures

**SB2-E-002** | Error Reporting
- Provide detailed error messages for debugging
- Include request IDs for support
- Log errors with appropriate severity levels
- Support error aggregation and analysis

## Configuration Requirements

### Environment Variables
```bash
NOTION_TOKEN                         # Primary API token
NOTION_WORKLOG_DATABASE_ID          # Worklog database UUID
NOTION_SUMMARIES_DATABASE_ID        # Summaries database UUID
NOTION_SCHEDULED_EVENTS_DATABASE_ID # Events database UUID
USER_FACTS_NOTION_DATABASE          # User facts database UUID
MCP_SERVERS_ENABLED=notion          # Enable MCP integration
```

### Database IDs (Production)
```python
STORYBOARD_DATABASE = "e02a1be2-549e43ff-8b0c-c3019ac99034"
PEOPLE_DATABASE = "b42279c9-42d1-495b-a6d7-45c87283dfe5"
NOTES_DATABASE = "26b90259-7ca5-42a6-b73a-a43a69c4851b"
```

## SignalBot2 Adapter Interface

The SignalBot2 adapter should provide high-level methods that abstract Notion complexity:

```python
class SignalBot2Adapter:
    # Worklog operations
    def log_activity(user, activity, category, duration=None, notes=None)
    def get_recent_activities(user=None, days=7)

    # Event scheduling
    def schedule_event(name, pattern, action, category=None)
    def get_upcoming_events(hours=24)
    def mark_event_executed(event_id, status, next_run)

    # User facts
    def store_fact(user, key, value, expires_in_days=None)
    def get_fact(user, key)
    def get_user_facts(user, category=None)

    # Summaries
    def store_summary(title, content, source, metadata)
    def search_summaries(query, limit=10)

    # Search
    def unified_search(query, databases=None, limit=50)
```

## Migration Path

1. **Phase 1**: Implement core operations maintaining backward compatibility
2. **Phase 2**: Add SignalBot2 adapter with high-level methods
3. **Phase 3**: Migrate from wsjd.at endpoints to direct API
4. **Phase 4**: Deprecate legacy code and optimize performance

## Success Criteria

- All existing SignalBot2 functionality continues working
- Performance is equal or better than current implementation
- MCP tools continue functioning without changes
- Migration can be done incrementally without downtime
- New features (data sources) are transparently handled