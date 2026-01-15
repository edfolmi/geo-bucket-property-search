## Troubleshooting

### Issue: GDAL library not found

**Error**: `django.core.exceptions.ImproperlyConfigured: Could not find the GDAL library`

**Solution**:
```bash
# 1. Install GDAL system library
# (See README.md → GDAL Installation section for OS-specific steps)

# 2. Find GDAL library location

# Linux:
find /usr -name "libgdal.so*" 2>/dev/null

# macOS:
find $(brew --prefix) -name "libgdal.dylib" 2>/dev/null

# Windows (PowerShell):
where gdal312.dll
# or
dir C:\OSGeo4W\bin\gdal*.dll

# 3. Set environment variable

# Linux / macOS:
export GDAL_LIBRARY_PATH=/path/to/libgdal.so  # or .dylib on macOS

# Windows (PowerShell):
setx GDAL_LIBRARY_PATH "C:\OSGeo4W\bin\gdal312.dll"

# Restart terminal after setting on Windows

# 4. Verify
python -c "from django.contrib.gis import gdal; print(gdal.HAS_GDAL)"
# Expected output: True
```

### Issue: `psycopg2` installation fails
```bash
# Linux (Ubuntu/Debian)
sudo apt-get install libpq-dev python3-dev

# macOS
brew install postgresql

# Windows
pip install psycopg2-binary
```

### Issue: PostGIS extension not found
```bash
# Linux
sudo apt-get install postgis postgresql-15-postgis-3

# macOS
brew install postgis

# Windows
# Use StackBuilder after installing PostgreSQL
# Select:
#  - Spatial Extensions
#  - PostGIS
# Then enable PostGIS in your database:

  `CREATE EXTENSION postgis;`
```

### Issue: GDAL version mismatch

**Error**: `RuntimeError: GDAL version mismatch`

**Solution**:
```bash
pip uninstall GDAL

# Linux / macOS
pip install GDAL==$(gdal-config --version)

# Windows
pip install GDAL
# Ensure OSGeo4W GDAL version matches the installed wheel
```

### Issue: Port 8000 already in use
```bash
# Use different port
python manage.py runserver 8001
```

### Issue: Database connection refused
```bash
# Linux
sudo systemctl status postgresql

# macOS
brew services list

# Windows
# Open Services
# Ensure "PostgreSQL" service is running

# Check credentials in .env file
```

### Issue: h3 library installation fails

**Solution**:
```bash
# Linux
sudo apt install build-essential

# macOS
xcode-select --install

# Windows
pip install --upgrade pip setuptools wheel
pip install h3
```
