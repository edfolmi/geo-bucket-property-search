# Quick Start Guide

Get up and running in 5 minutes!

## Prerequisites Checklist

- [ ] Python 3.11+ installed
- [ ] PostgreSQL 15+ installed
- [ ] PostGIS extension available
- [ ] GDAL library installed
- [ ] Git installed

## GDAL Quick Setup

**Before installing Python packages, install GDAL:**
```bash
# Linux
sudo apt install gdal-bin libgdal-dev
export GDAL_LIBRARY_PATH=/usr/lib/x86_64-linux-gnu/libgdal.so

# macOS
brew install gdal
export GDAL_LIBRARY_PATH=$(brew --prefix gdal)/lib/libgdal.dylib

# Verify
gdal-config --version
```

See README.md for detailed GDAL setup instructions.


## Setup Steps

### 1. Database Setup (2 minutes)

```bash
# Start PostgreSQL
sudo systemctl start postgresql  # Linux
brew services start postgresql   # macOS

# Create database and user
sudo -u postgres psql
```

```sql
CREATE DATABASE property_search;
CREATE USER property_user WITH PASSWORD 'property_pass';
GRANT ALL PRIVILEGES ON DATABASE property_search TO property_user;

\c property_search
CREATE EXTENSION postgis;
CREATE EXTENSION fuzzystrmatch;
GRANT ALL ON SCHEMA public TO property_user;
\q
```

### 2. Project Setup (1 minute)

```bash
# Clone/extract project
cd geo-bucket-property-search

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 3. Configure Environment (30 seconds)

```bash
# Copy environment template
cp .env.example .env

# Edit .env if needed (defaults work for local dev)
# DATABASE_NAME=property_search
# DATABASE_USER=property_user
# DATABASE_PASSWORD=property_pass
```

### 4. Initialize Database (1 minute)

```bash
cd src

# Run migrations
python manage.py migrate

# Load sample data
python manage.py shell < ../seed.py
```

### 5. Start Server (30 seconds)

```bash
# Start development server
python manage.py runserver

# Server running at: http://localhost:8000
```

## Test the API

### Create Property

```bash
curl -X POST http://localhost:8000/api/properties/ \
  -H "Content-Type: application/json" \
  -d '{
    "title": "3 Bedroom Flat",
    "location_name": "Sangotedo",
    "lat": 6.4698,
    "lng": 3.6285,
    "price": 15000000,
    "bedrooms": 3,
    "bathrooms": 2
  }'
```

### Search Properties

```bash
curl http://localhost:8000/api/properties/search?location=sangotedo
```

### Get Statistics

```bash
curl http://localhost:8000/api/geo-buckets/stats/
```

## Run Tests

```bash
# All tests
pytest

# With coverage
pytest --cov=properties --cov-report=html

# Specific test
pytest tests/test_location_matching.py -v
```

## Verify Installation

Expected results after seeding:

```bash
# Should show ~20 properties
curl http://localhost:8000/api/properties/ | jq '.count'

# Should show multiple buckets
curl http://localhost:8000/api/geo-buckets/stats/ | jq '.total_buckets'

# Should return Sangotedo properties
curl http://localhost:8000/api/properties/search?location=sangotedo | jq '.count'
```

## Common Issues

### Issue: `psycopg2` installation fails
```bash
# Install PostgreSQL development files
sudo apt-get install libpq-dev python3-dev  # Ubuntu
brew install postgresql                      # macOS
```

### Issue: PostGIS extension not found
```bash
# Install PostGIS
sudo apt-get install postgis postgresql-15-postgis-3  # Ubuntu
brew install postgis                                   # macOS
```

### Issue: Port 8000 already in use
```bash
# Use different port
python manage.py runserver 8001
```

### Issue: Database connection refused
```bash
# Check PostgreSQL is running
sudo systemctl status postgresql  # Linux
brew services list               # macOS

# Check credentials in .env file
```

## Next Steps

1. ✅ Read `DESIGN.md` for architecture details
2. ✅ Review `README.md` for comprehensive documentation
3. ✅ Explore code in `src/properties/`
4. ✅ Run tests to understand functionality

## Quick Commands Reference

```bash
# Development
python manage.py runserver            # Start server
python manage.py shell                # Django shell
python manage.py migrate              # Run migrations
python manage.py createsuperuser      # Create admin user

# Testing
pytest                                # Run all tests
pytest -v                             # Verbose output
pytest --cov                          # With coverage
pytest -k "test_name"                 # Specific test

# Database
python manage.py dbshell              # PostgreSQL shell
python manage.py shell < ../seed.py   # Reseed database
python manage.py flush                # Clear database

# Code Quality
black src/                            # Format code
flake8 src/                           # Lint code
mypy src/                             # Type checking
```

## Admin Interface

```bash
# Create superuser
python manage.py createsuperuser

# Access admin at:
http://localhost:8000/admin

# View properties and buckets in admin interface
```

## Project Structure Quick Reference

```
src/
├── properties/
│   ├── models.py           # Data models
│   ├── views.py           # API endpoints
│   ├── serializers.py     # Request/response serialization
│   └── services/          # Business logic
│       ├── bucket_service.py
│       ├── location_matcher.py
│       └── normalization.py
└── tests/                 # Test files
```

## API Endpoints Quick Reference

```
POST   /api/properties/                    # Create property
GET    /api/properties/                    # List properties
GET    /api/properties/{id}/               # Get property
PUT    /api/properties/{id}/               # Update property
DELETE /api/properties/{id}/               # Delete property
GET    /api/properties/search/?location=X  # Search by location

GET    /api/geo-buckets/                   # List buckets
GET    /api/geo-buckets/{id}/              # Get bucket
GET    /api/geo-buckets/stats/             # Get statistics
```

## Success Indicators

You're ready when:

- [ ] Server starts without errors
- [ ] Database has sample data
- [ ] All tests pass
- [ ] API returns expected results
- [ ] Search for "sangotedo" returns multiple properties

---

**Need Help?**
- Check logs: `tail -f src/property_search.log`
- Review error messages carefully
- Ensure all prerequisites are installed
- Verify database credentials
