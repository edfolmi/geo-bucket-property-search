# Geo-Bucket Location Normalization System - Architecture Design

## 1. Executive Summary

This system solves location inconsistency in property searches by implementing a geo-bucket approach that groups nearby properties into logical geographic clusters. It ensures searches for "Sangotedo", "sangotedo lagos", or "Sangotedo, Ajah" return consistent results.

## 2. Geo-Bucket Strategy

### 2.1 Bucket Definition
I use a **hybrid grid-based approach** with dynamic refinement:

- **Primary Grid**: H3 hexagonal grid system (resolution 9)
  - Cell size: ~174m diameter
  - Provides consistent, hierarchical geographic indexing
  - Efficient neighbor lookups

### 2.2 Bucket Grouping Logic

```
Bucket Creation Rules:
1. When a property is added, calculate its H3 index at resolution 9
2. Check if a bucket exists for this H3 cell
3. If no bucket exists:
   - Create new bucket with H3 index as identifier
   - Set centroid as the H3 cell center
   - Set name from normalized location string
4. If bucket exists:
   - Assign property to existing bucket
   - Update bucket statistics
```

### 2.3 Search Radius Strategy

- **Primary Search**: Exact H3 cell + immediate neighbors (7 cells total)
- **Expanded Search**: If results < 5, expand to ring-2 neighbors (19 cells)
- **Maximum Coverage**: ~500m radius from search point

### 2.4 Why This Approach?

**Advantages:**
- Consistent bucket boundaries (no arbitrary circles)
- Efficient spatial queries (O(1) cell lookup + O(k) neighbor scan)
- Hierarchical structure allows multi-resolution searches
- No need to recalculate buckets as data grows

**Trade-offs:**
- Fixed grid may split natural neighborhoods
- Mitigation: Always search bucket + neighbors

## 3. Database Schema

### 3.1 Core Tables

```sql
-- Geo-buckets for grouping nearby locations
CREATE TABLE geo_buckets (
    id SERIAL PRIMARY KEY,
    h3_index VARCHAR(15) UNIQUE NOT NULL,
    centroid GEOGRAPHY(POINT, 4326) NOT NULL,
    normalized_name VARCHAR(255) NOT NULL,
    variant_names TEXT[], -- Array of location name variations
    property_count INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Properties with geographic data
CREATE TABLE properties (
    id SERIAL PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    location_name VARCHAR(255) NOT NULL,
    location GEOGRAPHY(POINT, 4326) NOT NULL,
    bucket_id INTEGER REFERENCES geo_buckets(id) ON DELETE SET NULL,
    price DECIMAL(12, 2) NOT NULL,
    bedrooms INTEGER NOT NULL,
    bathrooms INTEGER NOT NULL,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Location name index for fuzzy matching
CREATE TABLE location_index (
    id SERIAL PRIMARY KEY,
    original_name VARCHAR(255) NOT NULL,
    normalized_name VARCHAR(255) NOT NULL,
    bucket_id INTEGER REFERENCES geo_buckets(id) ON DELETE CASCADE,
    metaphone VARCHAR(50), -- Phonetic encoding
    trigrams TEXT[], -- For fuzzy matching
    created_at TIMESTAMP DEFAULT NOW()
);
```

### 3.2 Indexes

```sql
-- Spatial indexes
CREATE INDEX idx_buckets_centroid ON geo_buckets USING GIST(centroid);
CREATE INDEX idx_properties_location ON properties USING GIST(location);
CREATE INDEX idx_buckets_h3 ON geo_buckets(h3_index);

-- Search optimization indexes
CREATE INDEX idx_buckets_normalized_name ON geo_buckets(normalized_name);
CREATE INDEX idx_location_index_normalized ON location_index(normalized_name);
CREATE INDEX idx_location_index_metaphone ON location_index(metaphone);
CREATE INDEX idx_properties_bucket ON properties(bucket_id);

-- GIN index for array operations
CREATE INDEX idx_buckets_variants ON geo_buckets USING GIN(variant_names);
CREATE INDEX idx_location_trigrams ON location_index USING GIN(trigrams);
```

### 3.3 Key Relationships

- **One-to-Many**: `geo_buckets` → `properties`
- **One-to-Many**: `geo_buckets` → `location_index`
- Properties are assigned to exactly one bucket based on coordinates
- Buckets track multiple name variations for fuzzy matching

## 4. Location Matching Logic

### 4.1 Multi-Layer Matching Strategy

```python
def find_matching_buckets(search_term: str, lat: float, lng: float) -> List[Bucket]:
    """
    Layer 1: Exact H3 Match (fastest)
    - Calculate H3 index for coordinates
    - Return bucket if exists
    
    Layer 2: Spatial + Normalized Name (primary)
    - Get H3 cell + neighbors (7 cells)
    - Filter by normalized name match (case-insensitive)
    - Return buckets within 500m radius
    
    Layer 3: Fuzzy Name Matching (fallback)
        Thresholds were empirically chosen to balance recall and precision for Nigerian location names, minimizing false positives like ‘Ajah’ vs ‘Agege’.
    - Use Levenshtein distance (threshold: 0.8 similarity)
    - Check metaphone phonetic encoding
    - Check trigram similarity (threshold: 0.6)
    
    Layer 4: Expanded Spatial (last resort)
    - Expand to ring-2 neighbors (19 cells)
    - Use broader name matching
    """
```

### 4.2 Name Normalization Process

```python
def normalize_location_name(name: str) -> str:
    """
    1. Convert to lowercase
    2. Remove special characters (keep alphanumeric and spaces)
    3. Remove common suffixes: "lagos", "nigeria", "lekki", etc.
    4. Collapse multiple spaces
    5. Trim whitespace
    6. Apply stemming for common variations
    
    Examples:
    - "Sangotedo, Ajah" → "sangotedo ajah"
    - "sangotedo lagos" → "sangotedo"
    - "Sangotedo" → "sangotedo"
    """
```

### 4.3 Proximity Thresholds

- **Exact Match**: Same H3 cell (~174m diameter)
- **Near Match**: Within 1-ring neighbors (~350m radius)
- **Extended Match**: Within 2-ring neighbors (~500m radius)
- **Coordinate Fuzzy Match**: Levenshtein distance ≤ 2 edits OR similarity ≥ 0.8

## 5. System Flow Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                        USER SEARCH REQUEST                       │
│              GET /api/properties/search?location=sangotedo       │
└───────────────────────────────┬─────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────┐
│                    LOCATION RESOLUTION LAYER                     │
├─────────────────────────────────────────────────────────────────┤
│  1. Normalize search term: "sangotedo" → "sangotedo"           │
│  2. Geocode (if no coords): "sangotedo" → (6.47, 3.63)         │
│  3. Calculate H3 index: h3_index = "891f1a64c7fffff"            │
└───────────────────────────────┬─────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────┐
│                      BUCKET MATCHING LAYER                       │
├─────────────────────────────────────────────────────────────────┤
│  Strategy:                                                       │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐         │
│  │ Exact H3     │→ │ Neighbor H3  │→ │ Fuzzy Name   │         │
│  │ Match        │  │ + Name Match │  │ Match        │         │
│  └──────────────┘  └──────────────┘  └──────────────┘         │
│                                                                  │
│  Result: [bucket_1, bucket_2, bucket_3]                         │
└───────────────────────────────┬─────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────┐
│                    PROPERTY RETRIEVAL LAYER                      │
├─────────────────────────────────────────────────────────────────┤
│  SELECT p.* FROM properties p                                    │
│  WHERE p.bucket_id IN (bucket_1, bucket_2, bucket_3)            │
│  ORDER BY p.created_at DESC                                      │
└───────────────────────────────┬─────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────┐
│                         RESPONSE LAYER                           │
├─────────────────────────────────────────────────────────────────┤
│  {                                                               │
│    "count": 47,                                                  │
│    "results": [                                                  │
│      {                                                           │
│        "id": 1,                                                  │
│        "title": "3 Bedroom Flat",                               │
│        "location_name": "Sangotedo",                            │
│        "bucket_name": "sangotedo",                              │
│        "price": 15000000,                                        │
│        ...                                                       │
│      }                                                           │
│    ]                                                             │
│  }                                                               │
└─────────────────────────────────────────────────────────────────┘
```

## 6. Property Creation Flow

```
┌─────────────────────────────────────────────────────────────────┐
│              POST /api/properties                                │
│  {                                                               │
│    "title": "3BR Flat",                                         │
│    "location_name": "Sangotedo, Ajah",                          │
│    "lat": 6.4720,                                               │
│    "lng": 3.6301,                                               │
│    "price": 15000000,                                            │
│    "bedrooms": 3,                                               │
│    "bathrooms": 2                                               │
│  }                                                               │
└───────────────────────────────┬─────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────┐
│                  BUCKET ASSIGNMENT LOGIC                         │
├─────────────────────────────────────────────────────────────────┤
│  1. Calculate H3 index from (lat, lng)                          │
│  2. Search for existing bucket with this H3 index               │
│  3. If found:                                                    │
│     - Assign property to bucket                                  │
│     - Add location_name to bucket variants if new               │
│     - Increment property_count                                   │
│  4. If not found:                                               │
│     - Create new bucket                                          │
│     - Set h3_index, centroid, normalized_name                   │
│     - Add to location_index                                      │
│     - Assign property to new bucket                             │
└───────────────────────────────┬─────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────┐
│                    DATABASE PERSISTENCE                          │
├─────────────────────────────────────────────────────────────────┤
│  BEGIN TRANSACTION;                                              │
│    INSERT INTO geo_buckets (...) ON CONFLICT DO NOTHING;        │
│    INSERT INTO properties (...);                                 │
│    INSERT INTO location_index (...);                             │
│    UPDATE geo_buckets SET property_count = property_count + 1;  │
│  COMMIT;                                                         │
└─────────────────────────────────────────────────────────────────┘
```

## 7. Scaling Considerations

### 7.1 Current Design (Up to 100K properties)
- Single PostgreSQL instance with PostGIS
- In-memory H3 calculations
- Standard B-tree and GiST indexes

### 7.2 Scaling to 500K Properties

**Database Optimization:**
- Partition `properties` table by bucket_id hash
- Implement read replicas for search queries
- Use materialized views for bucket statistics
- Add Redis cache for frequently searched buckets

**Application Layer:**
- Separate read/write API services
- Implement CDN for bucket metadata
- Add Elasticsearch for advanced text search
- Use message queue for async bucket recalculation

**Infrastructure:**
```
Load Balancer
    │
    ├─── API Service (Write) ──► Primary PostgreSQL
    │
    └─── API Service Pool (Read) ──► Read Replicas
              │                          │
              ├── Redis Cache            │
              └── Elasticsearch ─────────┘
```

### 7.3 Performance Targets
- Property creation: < 100ms (p95)
- Location search: < 50ms (p95)
- Bucket stats: < 200ms (cached)

## 8. Alternative Approaches Considered

### 8.1 Simple Radius Search
**Rejected because:**
- O(n) scan for every search
- No natural grouping mechanism
- Expensive distance calculations

### 8.2 QuadTree/R-Tree
**Rejected because:**
- Complex to maintain
- Rebalancing overhead
- Harder to reason about

### 8.3 Fixed Grid (Lat/Lng)
**Rejected because:**
- Poor coverage near poles (not relevant for Nigeria but affects portability)
- Inconsistent cell sizes
- H3 hexagons provide better neighbor uniformity

### 8.4 Chosen: H3 Hexagonal Grid
**Selected because:**
- Consistent cell shapes
- Efficient neighbor lookups
- Industry-proven (Uber, Meta use it)
- Easy to implement and understand

## 9. Assumptions

1. **Geographic Scope**: System targets Nigeria (Lagos area initially)
2. **Search Precision**: 500m radius is acceptable for "same area"
3. **Name Variations**: Limited to ~10 variations per bucket
4. **Update Frequency**: Properties are created >> searched
5. **Data Quality**: Coordinates are accurate within 100m

## 10. Future Improvements

1. **Machine Learning**: Train model on user search patterns to improve normalization
2. **Multi-language Support**: Handle Yoruba/Igbo location names
3. **Temporal Buckets**: Track bucket popularity over time
4. **Auto-merge**: Automatically merge under-utilized adjacent buckets
5. **User Feedback Loop**: Learn from searches that returned 0 results

## 11. Testing Strategy

### Unit Tests
- Location name normalization
- H3 index calculation
- Bucket assignment logic
- Fuzzy matching algorithms

### Integration Tests
- Property creation with bucket assignment
- Search across multiple bucket variants
- Boundary cases (edge of grid cells)

### Performance Tests
- 10K concurrent searches
- Batch property creation
- Large dataset queries (100K+ properties)

---

**Document Version**: 1.0  
**Last Updated**: January 2026  
**Author**: Senior Python Backend Engineer, Ephraim Daniel Folmi