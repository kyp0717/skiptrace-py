# Project Plan - Skip Trace Database System

## Updated: 2025-09-13

## Project Overview
Build a comprehensive web scraping and skip trace system that:
1. Scrapes foreclosure cases from Connecticut Judiciary website
2. Stores case and defendant data in Supabase database
3. Integrates with BatchData API for skip trace (phone lookup) services
4. Uses modern database schema with proper relationships

## Technology Stack
- **Language**: Python 3.x
- **Database**: Supabase (PostgreSQL)
- **Web Scraping**: Selenium, BeautifulSoup4
- **API Integration**: BatchData API (Sandbox & Production)
- **Testing**: Python unittest with uv virtual environment
- **Environment Management**: python-dotenv

## Database Schema (Final Version)

### Cases Table
```sql
CREATE TABLE cases (
    id SERIAL PRIMARY KEY,
    case_name VARCHAR(255) NOT NULL,
    docket_number VARCHAR(100) UNIQUE NOT NULL,  -- Primary reference key
    docket_url TEXT,
    town VARCHAR(100),
    created_at TIMESTAMP DEFAULT NOW()
);
```
- **Key Changes**:
  - Removed `search_date` and `updated_at` fields
  - `docket_number` serves as unique identifier for relationships

### Defendants Table
```sql
CREATE TABLE defendants (
    id SERIAL PRIMARY KEY,
    docket_number VARCHAR(100) NOT NULL REFERENCES cases(docket_number) ON DELETE CASCADE,
    name VARCHAR(255) NOT NULL,
    address TEXT,
    town VARCHAR(100),  -- Changed from 'city' to 'town'
    state VARCHAR(2),
    zip VARCHAR(10),
    created_at TIMESTAMP DEFAULT NOW(),
    UNIQUE(docket_number, name)
);
```
- **Key Changes**:
  - Uses `docket_number` as foreign key (not case_id)
  - Changed `city` field to `town` to match scraping data
  - Town is populated from the search parameter

### SkipTrace Table (formerly phone_numbers)
```sql
CREATE TABLE skiptrace (
    id SERIAL PRIMARY KEY,
    defendant_id INTEGER REFERENCES defendants(id) ON DELETE CASCADE,
    phone_number VARCHAR(20),
    phone_type VARCHAR(50),
    source VARCHAR(20) CHECK (source IN ('sandbox', 'production')),
    api_response JSONB,
    created_at TIMESTAMP DEFAULT NOW()
);
```
- **Key Changes**:
  - Renamed from `phone_numbers` to `skiptrace`
  - Stores complete skip trace results including API responses

## Project Structure
```
skip-trace-db/
├── src/                      # All Python source code
│   ├── case_scraper.py      # Web scraping logic
│   ├── db_connector.py      # Supabase database operations
│   ├── db_models.py         # Data models (Case, Defendant, SkipTrace)
│   ├── scraper_db_integration.py  # Integration layer
│   ├── batch_api_connector.py     # BatchData API integration
│   └── main.py              # Main application entry point
├── tests/                    # Test files
│   ├── test_db_connection.py
│   ├── test_site_connector.py
│   └── test_case_scraper.py
├── docs/                     # Documentation
│   ├── SUPABASE_SETUP.md
│   ├── SCHEMA_MIGRATION_V3.sql
│   └── database_setup.md
├── context/                  # Project context files (formerly prps/)
│   ├── project_plan_02.md   # This file
│   ├── tasks.md
│   └── requirements.md
├── logs/                     # Phase completion logs
├── scripts/                  # Utility scripts
├── .env                      # Environment variables (not in git)
├── .env.example             # Example environment template
├── requirements.txt         # Python dependencies
├── CLAUDE.md               # AI assistant instructions
└── README.md               # Project documentation
```

## Implementation Phases

### Phase 1 - Database Setup ✅
- Configure Supabase connection
- Create database schema with proper relationships
- Use `docket_number` as foreign key reference
- Implement `skiptrace` table for phone data

### Phase 2 - Web Scraping ✅
- Implement Connecticut Judiciary site scraper
- Extract case information by town
- Parse defendant names and addresses
- Store town name with defendant records

### Phase 3 - Database Integration ✅
- Create database models (Case, Defendant, SkipTrace)
- Implement CRUD operations
- Handle duplicate detection by docket_number
- Store scraped data with proper relationships

### Phase 4 - Skip Trace Integration (Pending)
- Integrate BatchData API (sandbox and production)
- Store skip trace results in `skiptrace` table
- Link phone numbers to defendants via defendant_id
- Support both sandbox and production environments

### Phase 5 - Testing & Validation ✅
- Unit tests for all components
- Integration tests with database
- Use uv for virtual environment management
- Colored test output (green/red)

## Key Design Decisions

1. **No case_id references**: System uses `docket_number` as the natural key for case-defendant relationships

2. **Town-based storage**: Defendants store the town name from the search, not parsed from address

3. **Simplified timestamps**: Only `created_at` is tracked, no `updated_at` or `search_date`

4. **SkipTrace naming**: Table renamed from `phone_numbers` to `skiptrace` to better reflect its purpose

5. **Folder structure**: All Python code in `src/`, tests in `tests/`, context files in `context/` (renamed from `prps/`)

## Command Line Usage

### Basic Scraping
```bash
# Scrape without database storage
python src/main.py Middletown

# Scrape and store in database
python src/main.py Middletown --db

# With skip trace (when implemented)
python src/main.py Middletown --db --skip-trace

# Production API (when implemented)
python src/main.py Middletown --db --skip-trace --prod
```

### Testing
```bash
# Run tests with uv
uv run python tests/test_db_connection.py

# Run main application with uv
uv run python src/main.py Middletown --db
```

## Environment Variables
```env
# Supabase Configuration
SUPABASE_URL=https://xxxxx.supabase.co
SUPABASE_ANON_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...

# BatchData API (Optional)
USE_SANDBOX=true
BATCHDATA_API_KEY=your_api_key_here
```

## Database Operations

### Core Functions in db_connector.py
- `insert_case()` - Add new foreclosure case
- `insert_defendant()` - Add defendant with docket_number reference
- `insert_skiptraces()` - Store skip trace phone results
- `get_case_by_docket()` - Retrieve case by docket number
- `get_defendants_by_docket()` - Get all defendants for a case
- `get_skiptraces_by_defendant()` - Get skip trace results
- `get_full_case_data()` - Complete case with defendants and skip traces

### Data Models in db_models.py
- `Case` - Court case information
- `Defendant` - Defendant with town field
- `SkipTrace` - Phone lookup results (formerly PhoneNumber)
- `ScrapedCase` - Web scraper output model

## Current Status (2025-09-13)

### Completed ✅
- Database schema design and implementation
- Web scraper for CT Judiciary site
- Supabase integration with proper relationships
- Test suite with colored output
- Successfully scraped and stored 83 Middletown cases
- Renamed tables and fields per requirements:
  - `phone_numbers` → `skiptrace`
  - `city` → `town` in defendants
  - Removed `search_date` and `updated_at`
  - Using `docket_number` as foreign key

### Pending Tasks
- BatchData API integration for skip trace
- Phone number lookup and storage in skiptrace table
- Production API endpoint support
- Batch processing optimizations
- Add more towns for scraping

## Migration Instructions

To apply the latest schema changes:

1. **Backup existing data** (if any)
2. **Run migration script** in Supabase SQL Editor:
   ```sql
   -- Use contents of docs/SCHEMA_MIGRATION_V3.sql
   ```
3. **Re-scrape data** with updated schema:
   ```bash
   uv run python src/main.py Middletown --db
   ```

## Success Metrics
- Successfully scrape all foreclosure cases for a given town
- Store complete case and defendant information
- Maintain data integrity with proper foreign key relationships
- Support both sandbox and production API environments
- All tests passing with proper virtual environment isolation
- Efficient duplicate detection using docket_number