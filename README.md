# Geo-Bucket Property Search System

A location normalization system for real estate property searches using geo-buckets to ensure consistent search results.

## Problem Statement

Users searching for properties in the same area get inconsistent results due to location name variations:
- "Sangotedo" → 0 results
- "sangotedo lagos" → 47 results  
- "Sangotedo, Ajah" → different results

This system solves this by grouping nearby properties into geo-buckets.

## Features

- ✅ Geo-bucket based location normalization using H3 hexagonal grid
- ✅ Fuzzy location name matching (case-insensitive, typo-tolerant)
- ✅ Automatic bucket assignment on property creation
- ✅ Efficient spatial queries with PostGIS
- ✅ RESTful API with Django Rest Framework
- ✅ Comprehensive test coverage

## Tech Stack

- **Backend**: Python 3.11+, Django 5.0, Django Rest Framework
- **Database**: PostgreSQL 15+ with PostGIS extension
- **Spatial Indexing**: H3 hexagonal grid (Uber's H3 library)
- **Testing**: pytest, pytest-django

## Prerequisites

- Python 3.11 or higher
- PostgreSQL 15+ with PostGIS extension
- GDAL library (required for spatial operations)
- pip and virtualenv

## 📌 GDAL Installation & Configuration

⚠️ **IMPORTANT**: This project depends on GDAL for spatial operations. You must install GDAL system library before installing Python dependencies.

### 🐧 Linux (Ubuntu/Debian)
```bash
# Install GDAL
sudo apt update
sudo apt install -y gdal-bin libgdal-dev

# Find the GDAL library path
gdal-config --libs
```

Set the GDAL library path (add to `~/.bashrc` or `~/.zshrc`):
```bash
# Example path - yours may differ
export GDAL_LIBRARY_PATH=/usr/lib/x86_64-linux-gnu/libgdal.so

# Apply changes
source ~/.bashrc
```

### 🍎 macOS (Homebrew)
```bash
# Install GDAL
brew install gdal

# Set GDAL library path
export GDAL_LIBRARY_PATH=$(brew --prefix gdal)/lib/libgdal.dylib

# Add to ~/.zshrc or ~/.bash_profile for persistence
echo 'export GDAL_LIBRARY_PATH=$(brew --prefix gdal)/lib/libgdal.dylib' >> ~/.zshrc
source ~/.zshrc
```

### 🪟 Windows (OSGeo4W)

1. Download and install [OSGeo4W](https://trac.osgeo.org/osgeo4w/)
2. During installation, select **GDAL** from available packages
3. Set environment variable (PowerShell as Administrator):
```powershell
setx GDAL_LIBRARY_PATH "C:\OSGeo4W\bin\gdal312.dll"
```

**Note**: DLL version number may vary (e.g., `gdal312.dll`, `gdal313.dll`). Check your `C:\OSGeo4W\bin\` directory.

4. **Restart your terminal** after setting the environment variable

### ✅ Verify GDAL Installation
```bash
# Check GDAL version
gdal-config --version

# On Windows (OSGeo4W Shell):
gdalinfo --version

# Verify environment variable is set
echo $GDAL_LIBRARY_PATH  # Linux/macOS
echo %GDAL_LIBRARY_PATH%  # Windows CMD
```

## Installation

### 1. Clone the Repository

```bash
git clone <repository-url>
cd geo-bucket-property-search
```

### 2. Set Up PostgreSQL with PostGIS

#### On Ubuntu/Debian:
```bash
sudo apt update
sudo apt install postgresql-15 postgresql-15-postgis-3
sudo systemctl start postgresql
```

#### On macOS:
```bash
brew install postgresql@15 postgis
brew services start postgresql@15
```

#### Create Database:
```bash
sudo -u postgres psql
```

```sql
CREATE DATABASE property_search;
CREATE USER property_user WITH PASSWORD 'property_pass';
ALTER ROLE property_user SET client_encoding TO 'utf8';
ALTER ROLE property_user SET default_transaction_isolation TO 'read committed';
ALTER ROLE property_user SET timezone TO 'UTC';
GRANT ALL PRIVILEGES ON DATABASE property_search TO property_user;

-- Connect to the database
\c property_search

-- Enable PostGIS
CREATE EXTENSION IF NOT EXISTS postgis;
CREATE EXTENSION IF NOT EXISTS fuzzystrmatch;

-- Grant schema privileges
GRANT ALL ON SCHEMA public TO property_user;
```

### 3. Set Up Python Environment

```bash
# Create virtual environment
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install --upgrade pip
pip install -r requirements.txt
```

### 4. Configure Environment Variables

Create a `.env` file in the project root:

```bash
# Database
DATABASE_NAME=property_search
DATABASE_USER=property_user
DATABASE_PASSWORD=property_pass
DATABASE_HOST=localhost
DATABASE_PORT=5432

# Django
SECRET_KEY=your-secret-key-here
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1
```

### 5. Run Migrations

```bash
cd src
python manage.py makemigrations
python manage.py migrate
```

### 6. Load Sample Data

```bash
# Run the seed script
python manage.py shell < ../seed.py

# Or use SQL seed file
psql -U property_user -d property_search -f ../seed.sql
```

## Running the Application

### Start Development Server

```bash
cd src
python manage.py runserver
```

The API will be available at `http://localhost:8000`

### API Endpoints

#### 1. Create Property
```bash
POST http://localhost:8000/api/properties/
Content-Type: application/json

{
  "title": "3 Bedroom Flat in Sangotedo",
  "location_name": "Sangotedo",
  "lat": 6.4698,
  "lng": 3.6285,
  "price": 15000000,
  "bedrooms": 3,
  "bathrooms": 2
}
```

#### 2. Search Properties
```bash
GET http://localhost:8000/api/properties/search?location=sangotedo
```

#### 3. Get Bucket Statistics
```bash
GET http://localhost:8000/api/geo-buckets/stats
```

## Running Tests

```bash
cd src

# Run all tests
pytest

# Run with coverage
pytest --cov=properties --cov-report=html

# Run specific test file
pytest tests/test_location_matching.py -v

# Run with detailed output
pytest -v -s
```

### Test Cases Covered

1. ✅ Property creation with automatic bucket assignment
2. ✅ Location search returns all variations (Sangotedo, sangotedo lagos, Sangotedo Ajah)
3. ✅ Case-insensitive matching
4. ✅ Fuzzy name matching (typo tolerance)
5. ✅ Spatial proximity grouping
6. ✅ Bucket statistics calculation

## Project Structure

```
.
├── src/
│   ├── property_search/          # Django project
│   │   ├── settings.py
│   │   ├── urls.py
│   │   └── wsgi.py
│   ├── properties/              # Main app
│   │   ├── models.py            # GeoBucket, Property models
│   │   ├── serializers.py       # DRF serializers
│   │   ├── views.py             # API views
│   │   ├── services/
│   │   │   ├── bucket_service.py      # Bucket management logic
│   │   │   ├── location_matcher.py    # Fuzzy matching
│   │   │   └── normalization.py       # Name normalization
│   │   └── migrations/
│   ├── tests/
│   │   ├── test_models.py
│   │   ├── test_services.py
│   │   ├── test_api.py
│   │   └── test_location_matching.py
|   ├── pytest.ini
│   └── manage.py
├── DESIGN.md                     # Architecture documentation
├── README.md                     # This file
├── requirements.txt              # Python dependencies
├── seed.sql                      # SQL seed data
└── seed.py                       # Python seed script
```

## Example Usage

### Create Properties with Different Variations

```bash
# Property 1: "Sangotedo"
curl -X POST http://localhost:8000/api/properties/ \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Modern 3BR Apartment",
    "location_name": "Sangotedo",
    "lat": 6.4698,
    "lng": 3.6285,
    "price": 15000000,
    "bedrooms": 3,
    "bathrooms": 2
  }'

# Property 2: "Sangotedo, Ajah"
curl -X POST http://localhost:8000/api/properties/ \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Luxury Duplex",
    "location_name": "Sangotedo, Ajah",
    "lat": 6.4720,
    "lng": 3.6301,
    "price": 25000000,
    "bedrooms": 4,
    "bathrooms": 3
  }'

# Property 3: "sangotedo lagos"
curl -X POST http://localhost:8000/api/properties/ \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Cozy 2BR Flat",
    "location_name": "sangotedo lagos",
    "lat": 6.4705,
    "lng": 3.6290,
    "price": 12000000,
    "bedrooms": 2,
    "bathrooms": 2
  }'
```

### Search Returns All Three

```bash
curl http://localhost:8000/api/properties/search?location=sangotedo

# Returns:
{
  "count": 3,
  "results": [
    {
      "id": 1,
      "title": "Modern 3BR Apartment",
      "location_name": "Sangotedo",
      "bucket_name": "sangotedo",
      ...
    },
    {
      "id": 2,
      "title": "Luxury Duplex",
      "location_name": "Sangotedo, Ajah",
      "bucket_name": "sangotedo",
      ...
    },
    {
      "id": 3,
      "title": "Cozy 2BR Flat",
      "location_name": "sangotedo lagos",
      "bucket_name": "sangotedo",
      ...
    }
  ]
}
```

## Performance

- Property creation: ~50ms (with bucket assignment)
- Location search: ~20ms (using spatial indexes)
- Handles 10K+ properties efficiently
- Scales to 500K+ with proposed optimizations (see DESIGN.md)

## Troubleshooting

### PostGIS Extension Not Found
```bash
sudo -u postgres psql property_search
CREATE EXTENSION IF NOT EXISTS postgis;
```

### H3 Library Issues
```bash
pip install --force-reinstall h3
```

### Migration Errors
```bash
python manage.py migrate --run-syncdb
```

### Port Already in Use
```bash
python manage.py runserver 8001
```

## Contributing

1. Write tests for new features
2. Follow PEP 8 style guide
3. Update documentation
4. Run tests before committing

## License

MIT License

## Contact

For questions or support, please contact the development team.

---

**Built with ❤️ by Edfolmi for better property search experiences**