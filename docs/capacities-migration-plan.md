# Notion to Capacities Migration Plan

## Overview

Migrate journalism workflow data from Notion to Capacities, a knowledge management system with better linking and AI capabilities.

## Goals

1. **Preserve all critical data** from Notion workspace
2. **Maintain relationships** between entities (projects, notes, people, tasks)
3. **Enable hybrid workflow** - allow both systems to coexist during transition
4. **Improve accessibility** - especially for Notes which are hard to access via Notion API

## Current Notion Structure

### Databases (7)

1. **📝 Projects (Storyboard)** - 77 properties
   - Main project/story tracking system
   - Includes publication tracking, team assignments, metrics

2. **🗒️ Notes** - 22 properties, 6,228 entries
   - Meeting notes, research, transcripts
   - Rich AI-generated summaries and takeaways
   - **PRIMARY MIGRATION TARGET** (not fully accessible via API)

3. **🛠️ Todos** - 21 properties
   - Task management with dependencies
   - Time estimates, priorities, blockers

4. **🫂 People** - 16 properties
   - Team members, contacts, sources
   - Bios, assignments, coverage areas

5. **💻 Assets** - 8 properties
   - Data sources, URLs, resources
   - IP addresses, descriptions

6. **🏷️ Tags** - 5 properties
   - Taxonomy/categorization

7. **💼 Worklog** - 6 properties
   - Time tracking entries

## Capacities API Capabilities

Based on `capacities-openapi.json`:

### Available Operations
- `/spaces` - Get/manage workspaces
- `/space-info` - Get structures (object types) and collections
- `/search` - Full-text and title search
- `/save-weblink` - Save URLs with metadata
- `/save-to-daily-note` - Append to daily notes

### Limitations
- **Read-only search** - can search but limited write operations
- **No bulk import** - must use daily notes or weblinks
- **Rate limits**: 5-120 req/min depending on endpoint
- **No direct database creation** - must set up structures in Capacities UI first

## Migration Strategy

### Phase 1: Structure Setup (Manual)
**Timeline: Day 1**

Create object types in Capacities UI:
1. **Projects** structure with properties:
   - Title, Summary, Status, Priority, Dates
   - Tags (native Capacities feature)

2. **Notes** structure with properties:
   - Title, Date, Summary, AI fields
   - Transcript/content blocks

3. **Tasks** structure:
   - Title, Status, Priority, Deadline

4. **People** structure:
   - Name, Email, Bio, Role

5. **Assets** structure:
   - Name, URL, Description

### Phase 2: Export Notion Data
**Timeline: Day 1-2**

✅ **COMPLETED**:
- Exported 556 HTML files from Notion Notes database
- Files in: `data/Private & Shared/Notes.../`

**TODO**:
- Query and export other databases via Notion API
- Extract structured data to JSON/CSV

### Phase 3: Data Transformation
**Timeline: Day 2-3**

Build Python scripts to:
1. Parse Notion HTML exports → structured data
2. Convert Notion properties → Capacities properties
3. Map relationships between entities
4. Handle special cases:
   - Transcription blocks (in HTML, not via API)
   - Rollup/formula fields
   - File attachments

### Phase 4: Import to Capacities
**Timeline: Day 3-5**

Implementation approaches:

**Option A: Daily Notes Import** (Fastest)
- Use `/save-to-daily-note` endpoint
- Append structured markdown to daily notes
- Include links to create objects
- **Pros**: Simple, works immediately
- **Cons**: Not structured, manual cleanup needed

**Option B: Structured Import** (Recommended)
- Set up structures in UI first
- Use search API to avoid duplicates
- Build custom import via web scraping if needed
- **Pros**: Clean, structured, relational
- **Cons**: May require reverse-engineering web API

**Option C: Hybrid** (Practical)
- Import Notes via daily notes with structured metadata
- Create Projects/People/Tasks manually or via web interface
- Link entities after import
- **Pros**: Balances speed and structure
- **Cons**: Some manual work

### Phase 5: Validation & Cleanup
**Timeline: Day 5-7**

- Verify all notes imported (6,228 entries)
- Check relationships preserved
- Test search functionality
- Document any data loss
- Create migration report

## Technical Implementation

### File Structure
```
notion-api/
├── capacities/
│   ├── __init__.py
│   ├── client.py           # Capacities API client
│   ├── structures.py       # Structure definitions
│   └── importer.py         # Migration logic
├── transformers/
│   ├── notion_html.py      # Parse Notion HTML exports
│   ├── notion_api.py       # Query Notion databases
│   └── capacities.py       # Transform to Capacities format
└── scripts/
    ├── export_notion.py    # Export all Notion data
    ├── migrate_notes.py    # Import Notes to Capacities
    └── migrate_all.py      # Full migration orchestration
```

### Key Classes

```python
class CapacitiesClient:
    """API client for Capacities"""
    def get_spaces()
    def get_space_info(space_id)
    def search(space_id, term)
    def save_to_daily_note(space_id, markdown, timestamp)

class NotionExporter:
    """Export data from Notion via API"""
    def export_database(db_id) -> List[Dict]
    def export_all() -> Dict[str, List[Dict]]

class NotionHTMLParser:
    """Parse Notion HTML exports"""
    def parse_file(path) -> Dict
    def extract_metadata(html) -> Dict
    def extract_content(html) -> str
    def extract_transcript(html) -> str

class CapacitiesImporter:
    """Import to Capacities"""
    def import_note(note_data)
    def import_project(project_data)
    def link_entities(mappings)
```

## Data Mapping

### Notes → Capacities Note Object

**Notion Properties** → **Capacities Properties**:
- Name → Title
- Date → Date
- AI Summary → Summary property
- AI Key Takeaways → Takeaways property
- AI Hammer → Headline property
- AI Deck → Deck property
- Details → Description
- Transcript block → Main content (markdown blocks)
- URL → Link property
- 📝 Projects → Project tag/link
- 🫂 People → People tags
- 🏷️ Tags → Native tags

### Projects → Capacities Project Object

- Name → Title
- Summary/AI Summary → Description
- Status → Status property
- Priority → Priority property
- Pub Date → Date property
- Hed/Dek → Title/Subtitle
- Notes → Backlinks to notes
- People → People tags
- Tags/Themes → Native tags

## Rate Limiting Strategy

From API docs:
- `/spaces`: 5 req/60sec
- `/space-info`: 5 req/60sec
- `/search`: 120 req/60sec
- `/save-to-daily-note`: 5 req/60sec

**Import Strategy**:
- Batch notes into groups of 5
- Wait 60 seconds between batches
- Use search to check for duplicates (faster rate limit)
- Estimated time: ~1200 minutes (20 hours) for 6,228 notes
- **Optimization**: Use daily note imports with multiple notes per call

## Rollback Plan

1. Keep Notion workspace intact during migration
2. Save all export data to `data/exports/`
3. Log all Capacities operations to `migration.log`
4. Create mapping file: `notion_id → capacities_id`
5. Document manual steps taken

## Success Criteria

- [ ] All 6,228 notes imported to Capacities
- [ ] All transcripts preserved with full content
- [ ] All AI-generated metadata preserved
- [ ] Relationships between entities maintained
- [ ] Search functionality working
- [ ] Zero data loss (validated by spot checks)

## Open Questions

1. **Structure Creation**: Can we create structures via API or only UI?
2. **Bulk Import**: Is there an undocumented bulk import API?
3. **File Attachments**: How to handle files in Notion exports?
4. **Rollup Fields**: Can Capacities replicate Notion's rollup functionality?
5. **API Keys**: Any limits on API key usage/quotas?

## Next Steps

1. Create GitHub issue for tracking
2. Create feature branch: `feat/capacities-migration`
3. Implement `CapacitiesClient` class
4. Test API connection and space access
5. Implement Note HTML parser
6. Run pilot import with 10 notes
7. Validate and iterate
