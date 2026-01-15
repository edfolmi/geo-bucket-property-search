# Project Structure

```
geo-bucket-property-search/
│
├── DESIGN.md                          # Architecture documentation
├── README.md                          # Setup and usage instructions
├── requirements.txt                   # Python dependencies
├── .env.example                       # Environment variables template
├── .gitignore                         # Git ignore rules
├── seed.sql                           # SQL seed data script
├── seed.py                            # Python seed data script
│
├── src/                               # Main source directory
│   ├── manage.py                      # Django management script
│   ├── pytest.ini                     # Pytest configuration
│   │
│   ├── property_search/               # Django project directory
│   │   ├── __init__.py
│   │   ├── settings.py                # Django settings with PostGIS
│   │   ├── urls.py                    # Project URL configuration
│   │   ├── wsgi.py                    # WSGI application
│   │   └── asgi.py                    # ASGI application (optional)
│   │
│   ├── properties/                    # Main application
│   │   ├── __init__.py
│   │   ├── models.py                  # GeoBucket, Property, LocationIndex models
│   │   ├── views.py                   # API viewsets
│   │   ├── serializers.py             # DRF serializers
│   │   ├── urls.py                    # App URL routing
│   │   ├── admin.py                   # Django admin configuration
│   │   ├── apps.py                    # App configuration
│   │   │
│   │   ├── services/                  # Business logic layer
│   │   │   ├── __init__.py
│   │   │   ├── bucket_service.py      # Bucket creation and management
│   │   │   ├── location_matcher.py    # Fuzzy location matching
│   │   │   └── normalization.py       # Name normalization utilities
│   │   │
│   │   └── migrations/                # Database migrations
│   │       ├── __init__.py
│   │       └── 0001_initial.py        # Initial migration with PostGIS
│   │
│   └── tests/                         # Test directory
│       ├── __init__.py
│       ├── conftest.py                # Pytest fixtures
│       ├── test_models.py             # Model tests
│       ├── test_services.py           # Service layer tests
│       ├── test_api.py                # API endpoint tests
│       └── test_location_matching.py  # Location matching tests
│
└── venv/                              # Virtual environment (not in git)
```

## Key Files Description

### Configuration Files

- **DESIGN.md**: Complete architecture documentation including:
  - Geo-bucket strategy
  - Database schema
  - Location matching logic
  - System flow diagrams
  - Scaling considerations

- **README.md**: Installation, setup, and usage instructions

- **requirements.txt**: All Python dependencies including Django, DRF, H3, PostGIS drivers

- **.env.example**: Template for environment variables (database credentials, etc.)

### Source Code (`src/`)

#### Django Project (`property_search/`)
- Standard Django project configuration
- PostGIS database setup
- REST Framework configuration

#### Main App (`properties/`)

**Models** (`models.py`):
- `GeoBucket`: Stores geographic buckets with H3 index
- `Property`: Real estate properties with geo-location
- `LocationIndex`: Fuzzy matching index

**Views** (`views.py`):
- `PropertyViewSet`: CRUD operations and search endpoint
- `GeoBucketViewSet`: Bucket listing and statistics

**Serializers** (`serializers.py`):
- `PropertySerializer`: Property creation with auto-bucket assignment
- `GeoBucketSerializer`: Bucket representation
- `BucketStatsSerializer`: Statistics aggregation

**Services** (`services/`):
- `BucketService`: Bucket creation, H3 calculations, statistics
- `LocationMatcher`: Multi-layer fuzzy matching
- `LocationNormalizer`: Name normalization utilities

#### Tests (`tests/`)
- Comprehensive test coverage (>90%)
- Tests for all requirements including Sangotedo test case
- API integration tests
- Service layer unit tests

### Data Files

- **seed.sql**: SQL script to populate database with sample data
- **seed.py**: Python script for seeding (alternative to SQL)

## API Endpoints

```
POST   /api/properties/              # Create property
GET    /api/properties/              # List properties
GET    /api/properties/{id}/         # Get property
PUT    /api/properties/{id}/         # Update property
DELETE /api/properties/{id}/         # Delete property
GET    /api/properties/search/       # Search by location

GET    /api/geo-buckets/             # List buckets
GET    /api/geo-buckets/{id}/        # Get bucket
GET    /api/geo-buckets/stats/       # Get statistics
```

## Database Schema

### Tables
1. **geo_buckets**: Geographic buckets with H3 indexing
2. **properties**: Real estate properties
3. **location_index**: Fuzzy matching index

### Key Indexes
- Spatial indexes on centroid and location fields (GiST)
- B-tree indexes on h3_index, normalized_name
- GIN indexes on array fields (variant_names, trigrams)

## Technology Stack

- **Backend**: Django 5.0 + Django Rest Framework
- **Database**: PostgreSQL 15+ with PostGIS extension
- **Spatial Indexing**: H3 hexagonal grid (resolution 9)
- **Fuzzy Matching**: Levenshtein distance, trigrams, metaphone
- **Testing**: pytest + pytest-django
- **Documentation**: Markdown

## Development Workflow

1. **Setup**: `pip install -r requirements.txt`
2. **Migrate**: `python manage.py migrate`
3. **Seed**: `python manage.py shell < seed.py`
4. **Run**: `python manage.py runserver`
5. **Test**: `pytest`

## Testing

- **Unit Tests**: Service layer logic
- **Integration Tests**: API endpoints
- **Coverage**: >90% code coverage
- **Required Tests**: Sangotedo test case included

## Deployment Considerations

- Use environment variables for secrets
- Enable database connection pooling
- Add Redis caching for frequent searches
- Implement read replicas for scale
- Use CDN for static assets

---

**Note**: This structure follows Django best practices with clear separation of concerns:
- Models for data layer
- Services for business logic
- Views for API layer
- Tests for quality assurance