# Project Plan 03 - Remaining Backend Development Phases

## Document Version: 2.0
## Created: 2025-09-15
## Updated: 2025-09-15
## Purpose: Remaining Backend System Development Roadmap

## Executive Summary

This document outlines the remaining backend development phases for the Foreclosure Scraper and Skip Trace system. Building upon the completed work from project_plan_01.md and project_plan_02.md, this plan focuses on enhancing the existing system with production-ready features including API development, background processing, authentication, monitoring, and deployment.

## Completed Work Summary (from Plans 01 & 02)

### Already Implemented ✅
- **Web Scraping**: Selenium + BeautifulSoup4 scraper for CT Judiciary site
- **Database**: Supabase PostgreSQL with tables (cases, defendants, skiptrace)
- **Data Models**: Case, Defendant, SkipTrace, ScrapedCase models
- **Database Operations**: CRUD operations in db_connector.py
- **API Integration**: BatchData API (sandbox and production modes)
- **CLI Application**: main.py with --db and --skip-trace flags
- **Web Interface**: Basic Flask application with templates
- **Integration Modules**:
  - scraper_db_integration.py
  - skip_trace_integration.py
- **Testing**: Comprehensive test suite for all components
- **Configuration**: Environment variables, requirements.txt

### Current System Capabilities
1. Scrape foreclosure cases by town from CT Judiciary website
2. Store case and defendant data in Supabase
3. Perform skip trace lookups via BatchData API
4. Display data through Flask web interface
5. Run via CLI with various options

## Remaining Backend Architecture

### Technology Stack Additions Needed
```
Current Stack           →  Enhanced Stack
─────────────             ─────────────
Flask (basic)          →  FastAPI + Flask (transition)
No task queue          →  Celery + Redis
No caching             →  Redis caching layer
Basic logging          →  Structured logging + monitoring
No auth                →  JWT/Supabase Auth
Manual deployment      →  Docker + CI/CD
```

## Development Phases

### Phase 1: Connecticut Towns and Counties Data Scraper
**Duration**: 3-4 days
**Priority**: High
**Dependencies**: None

#### Objectives
- Scrape comprehensive list of Connecticut towns and their associated counties
- Create a reference database table for town-county mappings
- Enhance existing scraper to validate town names
- Provide autocomplete/dropdown data for UI

#### Target Website
- **URL**: https://libguides.ctstatelibrary.org/cttowns
- **Content**: Complete list of 169 Connecticut towns organized by 8 counties

#### Implementation Plan
```python
# New files to create:
src/
├── town_county_scraper.py   # Scraper for CT State Library
├── town_validator.py         # Validate and normalize town names
└── db/
    └── town_county_loader.py # Load data into database

# Database table to add:
CREATE TABLE town_counties (
    id SERIAL PRIMARY KEY,
    town_name VARCHAR(100) UNIQUE NOT NULL,
    county VARCHAR(50) NOT NULL,
    town_normalized VARCHAR(100),  -- For fuzzy matching
    population INTEGER,             -- If available
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

# Add index for fast lookups
CREATE INDEX idx_town_normalized ON town_counties(town_normalized);
CREATE INDEX idx_county ON town_counties(county);
```

#### Data Structure to Extract
```json
{
  "counties": {
    "Fairfield": ["Bethel", "Bridgeport", "Brookfield", "Danbury", ...],
    "Hartford": ["Avon", "Berlin", "Bloomfield", "Bristol", ...],
    "Litchfield": ["Barkhamsted", "Bethlehem", "Bridgewater", ...],
    "Middlesex": ["Chester", "Clinton", "Cromwell", ...],
    "New Haven": ["Ansonia", "Beacon Falls", "Bethany", ...],
    "New London": ["Bozrah", "Colchester", "East Lyme", ...],
    "Tolland": ["Andover", "Bolton", "Columbia", ...],
    "Windham": ["Ashford", "Brooklyn", "Canterbury", ...]
  }
}
```

#### Features to Implement
1. **Web Scraper**
   - Parse HTML table from CT State Library page
   - Extract town names and county associations
   - Handle special characters and formatting
   - Cache results to avoid repeated scraping

2. **Data Validation**
   - Normalize town names (handle "Town of X" vs "X")
   - Create fuzzy matching for user input
   - Validate against official list

3. **Database Integration**
   - Store town-county mappings
   - Update existing cases with validated town names
   - Provide lookup functions

4. **API Endpoints** (to add in Phase 2)
   ```
   GET /api/v1/towns              # List all towns
   GET /api/v1/towns/{county}     # Towns by county
   GET /api/v1/counties           # List all counties
   GET /api/v1/towns/search?q=    # Fuzzy search towns
   ```

#### Tasks
1. Create `town_county_scraper.py` using BeautifulSoup
2. Parse and extract town-county data from website
3. Create database migration for `town_counties` table
4. Implement data loader to populate database
5. Create validation functions for town names
6. Update existing scrapers to validate town input
7. Add caching mechanism for scraped data
8. Write comprehensive tests

#### Integration with Existing System
- Enhance `case_scraper.py` to validate town names
- Update `main.py` to use validated town list
- Add town autocomplete to Flask web interface
- Create data quality reports for existing records

#### Deliverables
- Town/county scraper module
- Database table with all CT towns and counties
- Town validation utility functions
- Updated scrapers with validation
- Test suite for new functionality
- Documentation on town data structure

---

### Phase 2: RESTful API Development with FastAPI
**Duration**: 1.5 weeks
**Priority**: High
**Dependencies**: Phase 1 (for towns endpoints)

#### Objectives
- Create production-ready REST API
- Maintain backward compatibility with Flask during transition
- Implement proper API standards and documentation

#### Implementation Plan
```python
# New file structure to add:
src/
├── api/
│   ├── __init__.py
│   ├── main.py          # FastAPI app
│   ├── dependencies.py  # Shared dependencies
│   └── v1/
│       ├── endpoints/
│       │   ├── cases.py
│       │   ├── defendants.py
│       │   ├── skiptraces.py
│       │   └── scraper.py
│       └── schemas/
│           ├── case.py
│           ├── defendant.py
│           └── skiptrace.py
```

#### API Endpoints to Implement
```
/api/v1/towns
  GET    /                    # List all CT towns
  GET    /by-county/{county}  # Get towns by county
  GET    /search              # Fuzzy search towns
  GET    /validate/{name}     # Validate town name

/api/v1/counties
  GET    /                    # List all CT counties
  GET    /{county}/stats      # Get county statistics

/api/v1/cases
  GET    /                    # List cases (paginated)
  GET    /{docket_number}     # Get single case
  POST   /                    # Create case
  PUT    /{docket_number}     # Update case
  DELETE /{docket_number}     # Delete case
  GET    /search              # Search cases
  GET    /by-town/{town}      # Get cases by town

/api/v1/defendants
  GET    /                    # List defendants
  GET    /{id}                # Get defendant
  GET    /by-case/{docket}    # Get defendants by case
  PUT    /{id}                # Update defendant

/api/v1/skiptraces
  POST   /lookup              # Trigger skip trace
  GET    /history             # Get skip trace history
  GET    /by-defendant/{id}   # Get traces by defendant
  GET    /costs               # Get cost summary

/api/v1/scraper
  POST   /scrape              # Start scraping job
  GET    /status/{job_id}     # Get job status
  GET    /history             # Get scraping history
```

#### Tasks
1. Install FastAPI dependencies
2. Create FastAPI application structure
3. Implement Pydantic schemas from existing models
4. Build CRUD endpoints for each entity
5. Add request validation and error handling
6. Implement pagination and filtering
7. Set up automatic API documentation
8. Create API testing suite

#### Deliverables
- FastAPI application in `src/api/`
- Pydantic schemas for validation
- Auto-generated API docs at `/docs`
- API test suite
- Migration guide from Flask

---

### Phase 3: Background Job Processing with Celery
**Duration**: 1 week
**Priority**: High
**Dependencies**: Redis installation

#### Objectives
- Implement asynchronous task processing for long-running operations
- Create scheduled jobs for automation
- Add job monitoring and management

#### Background Tasks to Implement
```python
# src/tasks/
├── __init__.py
├── celery_app.py
├── scraping_tasks.py
│   ├── scrape_town_async()
│   ├── scrape_multiple_towns()
│   ├── scrape_all_ct_towns()      # New: scrape all 169 towns
│   ├── update_case_details()
│   └── validate_town_data()        # New: validate town names
├── skiptrace_tasks.py
│   ├── batch_skip_trace()
│   ├── process_skip_trace_queue()
│   └── retry_failed_traces()
├── town_tasks.py                   # New: town-related tasks
│   ├── update_town_county_data()
│   ├── sync_town_statistics()
│   └── generate_town_reports()
└── maintenance_tasks.py
    ├── cleanup_old_sessions()
    ├── generate_daily_report()
    └── backup_database()
```

#### Scheduled Jobs
- **Daily**:
  - Scrape configured towns at 2 AM
  - Update town/county data from CT State Library
- **Hourly**: Process pending skip traces
- **Weekly**:
  - Generate cost reports
  - Validate all town names in database
- **Monthly**:
  - Clean up old data
  - Generate town statistics report

#### Tasks
1. Set up Redis as message broker
2. Configure Celery with Redis backend
3. Convert long-running operations to async tasks
4. Implement task retry logic
5. Create task monitoring endpoints
6. Add scheduled job configurations
7. Build task management UI

#### Deliverables
- Celery configuration and tasks
- Task monitoring dashboard
- Scheduled job documentation
- Worker deployment scripts

---

### Phase 4: Authentication & Authorization System
**Duration**: 1 week
**Priority**: Medium
**Dependencies**: Phase 2 (API)

#### Objectives
- Implement secure user authentication
- Add role-based access control
- Protect API endpoints
- Create user management system

#### User Roles & Permissions
```
Admin
├── Full system access
├── User management
├── Cost configuration
└── System settings

Manager
├── View all data
├── Trigger scraping
├── Run skip traces
└── Export reports

Viewer
├── View data only
├── No write operations
└── Limited exports

API User
├── Programmatic access
├── Rate limited
└── Specific endpoints only
```

#### Implementation
1. **Authentication Method**: JWT tokens with Supabase Auth
2. **Session Management**: Redis-based sessions
3. **API Security**: Bearer token authentication
4. **Password Policy**: Bcrypt hashing, complexity requirements

#### Tasks
1. Integrate Supabase Auth or implement JWT
2. Create user registration/login endpoints
3. Implement role-based middleware
4. Add permission decorators to endpoints
5. Create user management CRUD operations
6. Implement password reset flow
7. Add API key generation for programmatic access
8. Create audit logging for sensitive operations

#### Deliverables
- Authentication endpoints
- User management system
- Role-based access control
- Security documentation

---

### Phase 5: Enhanced Database Layer
**Duration**: 1 week
**Priority**: Medium
**Dependencies**: None

#### Objectives
- Add missing database tables
- Implement database migrations
- Optimize query performance
- Add caching layer

#### New Tables to Add
```sql
-- User management
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255),
    role VARCHAR(50),
    api_key VARCHAR(255) UNIQUE,
    created_at TIMESTAMP DEFAULT NOW(),
    last_login TIMESTAMP
);

-- API usage tracking
CREATE TABLE api_logs (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id),
    endpoint VARCHAR(255),
    method VARCHAR(10),
    status_code INTEGER,
    response_time_ms INTEGER,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Scraping sessions
CREATE TABLE scrape_sessions (
    id SERIAL PRIMARY KEY,
    town VARCHAR(100),
    status VARCHAR(50),
    cases_found INTEGER,
    started_at TIMESTAMP,
    completed_at TIMESTAMP,
    error_message TEXT
);

-- Cost tracking
CREATE TABLE cost_tracking (
    id SERIAL PRIMARY KEY,
    service VARCHAR(50),
    operation VARCHAR(100),
    quantity INTEGER,
    unit_cost DECIMAL(10,4),
    total_cost DECIMAL(10,2),
    user_id INTEGER REFERENCES users(id),
    created_at TIMESTAMP DEFAULT NOW()
);
```

#### Performance Optimizations
1. Add database indexes for frequent queries
2. Implement query result caching with Redis
3. Add database connection pooling
4. Create materialized views for reports

#### Tasks
1. Create Alembic migration system
2. Write migration scripts for new tables
3. Add indexes to optimize queries
4. Implement Redis caching layer
5. Create database backup automation
6. Add query performance monitoring

#### Deliverables
- Database migration scripts
- Caching implementation
- Performance benchmarks
- Backup procedures

---

### Phase 6: Monitoring, Logging & Analytics
**Duration**: 1 week
**Priority**: Medium
**Dependencies**: Phases 2-4

#### Objectives
- Implement structured logging
- Add application monitoring
- Create analytics dashboard
- Set up alerting system

#### Monitoring Stack
```
Application Metrics
├── API response times
├── Database query performance
├── Task execution times
├── Error rates
└── Resource usage

Business Metrics
├── Cases scraped per day
├── Skip traces performed
├── API usage by endpoint
├── Cost per operation
└── User activity

System Health
├── Service availability
├── Queue depths
├── Cache hit rates
├── Database connections
└── Memory/CPU usage
```

#### Implementation Tools
- **Logging**: Python logging + Loguru
- **Metrics**: Prometheus + Grafana
- **Error Tracking**: Sentry
- **APM**: OpenTelemetry (optional)

#### Tasks
1. Configure structured logging with Loguru
2. Add request/response logging middleware
3. Implement metrics collection
4. Set up Grafana dashboards
5. Configure Sentry for error tracking
6. Create custom analytics queries
7. Set up alerting rules
8. Document monitoring procedures

#### Deliverables
- Logging configuration
- Monitoring dashboards
- Alert configurations
- Operations runbook

---

### Phase 7: Testing & Quality Assurance
**Duration**: 1 week (ongoing throughout)
**Priority**: High
**Dependencies**: All phases

#### Objectives
- Achieve 80% test coverage
- Implement integration tests
- Create load testing suite
- Set up CI/CD pipeline

#### Testing Strategy
```
Unit Tests (Target: 85% coverage)
├── API endpoints
├── Database operations
├── Background tasks
├── Business logic
└── Utility functions

Integration Tests
├── API workflows
├── Database transactions
├── Task processing
├── Authentication flows
└── Skip trace integration

Performance Tests
├── Load testing (Locust)
├── Stress testing
├── Database benchmarks
└── API latency tests
```

#### CI/CD Pipeline
```yaml
# GitHub Actions workflow
on: [push, pull_request]
jobs:
  test:
    - Run unit tests
    - Run integration tests
    - Check code coverage
    - Run linting (pylint, black)
    - Security scanning
  deploy:
    - Build Docker images
    - Run migrations
    - Deploy to staging
    - Run smoke tests
    - Deploy to production
```

#### Tasks
1. Write missing unit tests
2. Create integration test suite
3. Set up load testing with Locust
4. Configure GitHub Actions CI/CD
5. Add code quality checks
6. Create test data fixtures
7. Document testing procedures

#### Deliverables
- Complete test suite
- CI/CD pipeline configuration
- Load testing reports
- Testing documentation

---

### Phase 8: Deployment & Infrastructure
**Duration**: 1 week
**Priority**: High
**Dependencies**: All phases

#### Objectives
- Containerize application
- Set up production infrastructure
- Implement deployment pipeline
- Create monitoring and backup strategies

#### Deployment Architecture
```
Docker Containers
├── api (FastAPI application)
├── worker (Celery workers)
├── scheduler (Celery beat)
├── redis (Cache and queue)
└── nginx (Reverse proxy)

Deployment Options
├── Cloud Run (Google Cloud)
├── ECS (AWS)
├── Heroku (Simple option)
└── VPS (Cost-effective)
```

#### Infrastructure as Code
```yaml
# docker-compose.yml for local/staging
services:
  api:
    build: .
    ports: ["8000:8000"]
    environment:
      - DATABASE_URL
      - REDIS_URL

  worker:
    build: .
    command: celery worker
    environment:
      - DATABASE_URL
      - REDIS_URL

  scheduler:
    build: .
    command: celery beat

  redis:
    image: redis:alpine
    ports: ["6379:6379"]
```

#### Tasks
1. Create Dockerfile for application
2. Write docker-compose configuration
3. Set up container registry
4. Configure production environment
5. Implement blue-green deployment
6. Set up SSL certificates
7. Create backup procedures
8. Document deployment process

#### Deliverables
- Docker configuration files
- Deployment scripts
- Infrastructure documentation
- Disaster recovery plan

---

## Implementation Timeline

### Gantt Chart (9-week plan)
```
Week 1:   Phase 1 - Town/County Scraper
Week 2-3: Phase 2 - FastAPI Development
Week 3-4: Phase 3 - Celery Background Jobs
Week 4-5: Phase 4 - Authentication System
Week 5-6: Phase 5 - Database Enhancement
Week 6-7: Phase 6 - Monitoring & Logging
Week 7-8: Phase 7 - Testing & QA
Week 8-9: Phase 8 - Deployment
```

### Parallel Execution Strategy
- Phase 1 should complete first (foundation data)
- Phase 2 & 5 can run in parallel after Phase 1
- Phase 3 can start after Phase 2 API structure is ready
- Phase 4 depends on Phase 2 completion
- Phase 6 & 7 are ongoing throughout
- Phase 8 requires all other phases

## Resource Requirements

### Development Resources
- **Backend Developer**: 1 (full-time)
- **DevOps Support**: 0.5 (part-time)
- **QA/Testing**: 0.5 (part-time)

### Infrastructure Costs (Monthly)
```
Development:
- Supabase: Free tier
- Redis: Local Docker
- Total: $0

Production:
- Supabase: $25 (Pro plan)
- Redis Cloud: $5 (basic)
- Hosting: $20-50 (varies)
- Domain/SSL: $2
- Monitoring: $10 (optional)
- Total: ~$62-92/month
```

### Required Tools
- Docker Desktop
- Redis (local or cloud)
- Python 3.10+
- PostgreSQL client
- Postman/Insomnia

## Risk Mitigation

### Technical Risks
1. **Migration Complexity**: Gradual migration from Flask to FastAPI
2. **Performance Issues**: Implement caching and optimization early
3. **Security Vulnerabilities**: Regular security audits and updates
4. **Data Loss**: Automated backups and disaster recovery

### Mitigation Strategies
- Maintain backward compatibility during transitions
- Implement comprehensive testing at each phase
- Use feature flags for gradual rollouts
- Regular code reviews and security scans

## Success Criteria

### Technical Metrics
- API response time < 200ms (p95)
- Test coverage > 80%
- Zero critical security vulnerabilities
- 99.9% uptime

### Business Metrics
- Support 100+ concurrent users
- Process 1000+ skip traces per day
- Reduce manual operations by 80%
- Cost per operation < $0.10

## Next Steps

### Immediate Actions (Week 1)
1. Implement CT towns/counties scraper
2. Create town_counties database table
3. Populate database with town data
4. Update existing scrapers with validation

### Week 2-3 Priorities
1. Set up FastAPI project structure
2. Create API endpoints including towns/counties
3. Implement Pydantic schemas
4. Begin Celery setup for background tasks

### Documentation Requirements
1. API documentation (auto-generated)
2. Deployment guide
3. Operations runbook
4. User guide updates

## Conclusion

This plan builds upon the solid foundation established in phases 1 and 2, focusing on transforming the current system into a production-ready, scalable backend. The phased approach allows for gradual enhancement while maintaining system stability and backward compatibility.

## Document History
- v1.0 (2025-09-15): Initial backend development plan
- v2.0 (2025-09-15): Updated to focus on remaining work only
- v2.1 (2025-09-15): Added Phase 1 for CT towns/counties scraper