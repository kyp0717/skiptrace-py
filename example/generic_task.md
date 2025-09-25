# Project Tasks

## Status Legend
- ✅ Completed
- 🔄 In Progress
- ⏳ Pending
- ❌ Blocked

## Phase 1: Core Scraping Implementation

### Infrastructure & Setup
- ✅ Set up Rust project with required dependencies (2025-08-06)
- ✅ Implement basic Selenium WebDriver integration (2025-08-06)
- ✅ Create Case struct and Cases collection (2025-08-06)
- ⏳ Create tasks.md tracking file (2025-08-06)

### Data Extraction
- ✅ Implement scraping case list from property search (2025-08-06)
- ✅ Extract case docket numbers from search results (2025-08-06)
- ✅ Navigate to individual case detail pages (2025-08-06)
- ✅ Extract defendant names from case details (2025-08-06)
- ✅ Extract property addresses from case details (2025-08-06)

### Code Quality & Organization
- ⏳ Refactor main.rs to separate concerns
- ⏳ Create dedicated scraper module
- ⏳ Implement configuration management (.env file)
- ⏳ Add proper error handling and retry logic
- ⏳ Remove hardcoded values (city, port, limits)

### Data Export & Storage
- ⏳ Implement CSV export functionality
- ⏳ Add JSON export option
- ⏳ Implement data persistence/caching

### Testing
- ⏳ Create unit tests for Case extraction
- ⏳ Add integration tests for scraper
- ⏳ Test error handling scenarios

## Phase 2: Phone Number Search

### People Search Integration
- ✅ Research and select people search API/service (2025-08-09) - Using TruePeopleSearch.com
- ✅ Implement phone number lookup by name/address (2025-08-09)
- ✅ Handle multiple match scenarios (2025-08-09)
- ✅ Add rate limiting for API calls (2025-08-09)
- ✅ Store phone numbers with confidence scores (2025-08-09)

## Phase 3: Testing & Deployment

### Comprehensive Testing
- ⏳ End-to-end testing of complete workflow
- ⏳ Performance testing with large datasets
- ⏳ Test with multiple cities/towns
- ⏳ Validate data accuracy

### Deployment & Documentation
- ⏳ Create comprehensive README
- ⏳ Add usage examples
- ⏳ Document API keys/configuration
- ⏳ Create Docker container (optional)
- ⏳ Set up CI/CD pipeline (optional)

## Discovered During Work

### Immediate Issues
- Hardcoded city name "Middletown" in main.rs:25
- Hardcoded WebDriver port "46107" in main.rs:15
- Arbitrary limit of 5 cases in main.rs:79
- CSV export code is commented out in main.rs:83

### Technical Debt
- No error recovery for failed WebDriver connections
- No handling for missing HTML elements
- No logging/debugging output beyond println!
- Case files saved to root directory (should use output folder)

### Phase 2 Implementation Notes
- ✅ Created phone_lookup.rs module with PhoneLookup struct (2025-08-09)
- ✅ Integrated TruePeopleSearch.com web scraping (2025-08-09)
- ✅ Added phone_numbers field to Case struct (2025-08-09)
- ✅ Implemented confidence scoring for phone number matches (2025-08-09)
- ✅ Added rate limiting with configurable delay (2025-08-09)
- ✅ Updated CSV export to include phone numbers (2025-08-09)

## Notes
- Project uses Selenium WebDriver (requires running instance)
- Currently scrapes Connecticut Judicial civil inquiry site
- Extracts: case name, docket number, defendant, property address
- Next priority: Remove hardcoded values and add configuration