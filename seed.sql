-- Seed data for Property Search System
-- This script populates the database with sample properties including Sangotedo variations

-- Enable PostGIS if not already enabled
CREATE EXTENSION IF NOT EXISTS postgis;

-- Clean existing data
TRUNCATE TABLE properties, location_index, geo_buckets RESTART IDENTITY CASCADE;

-- Insert Sangotedo properties (THE REQUIRED TEST CASE)
-- These should all return when searching for "sangotedo"

-- Property 1: "Sangotedo"
INSERT INTO properties (title, location_name, location, price, bedrooms, bathrooms, created_at, updated_at)
VALUES (
    'Modern 3BR Apartment in Sangotedo',
    'Sangotedo',
    ST_SetSRID(ST_MakePoint(3.6285, 6.4698), 4326),
    15000000.00,
    3,
    2,
    NOW(),
    NOW()
);

-- Property 2: "Sangotedo, Ajah"
INSERT INTO properties (title, location_name, location, price, bedrooms, bathrooms, created_at, updated_at)
VALUES (
    'Luxury 4BR Duplex',
    'Sangotedo, Ajah',
    ST_SetSRID(ST_MakePoint(3.6301, 6.4720), 4326),
    25000000.00,
    4,
    3,
    NOW(),
    NOW()
);

-- Property 3: "sangotedo lagos"
INSERT INTO properties (title, location_name, location, price, bedrooms, bathrooms, created_at, updated_at)
VALUES (
    'Cozy 2BR Flat',
    'sangotedo lagos',
    ST_SetSRID(ST_MakePoint(3.6290, 6.4705), 4326),
    12000000.00,
    2,
    2,
    NOW(),
    NOW()
);

-- Additional Sangotedo variations
INSERT INTO properties (title, location_name, location, price, bedrooms, bathrooms, created_at, updated_at)
VALUES (
    'Executive 5BR Mansion',
    'Sangotedo Lekki',
    ST_SetSRID(ST_MakePoint(3.6295, 6.4710), 4326),
    45000000.00,
    5,
    4,
    NOW(),
    NOW()
);

-- Lekki Phase 1 Properties
INSERT INTO properties (title, location_name, location, price, bedrooms, bathrooms, created_at, updated_at)
VALUES 
    (
        'Luxury 3BR Waterfront Apartment',
        'Lekki Phase 1',
        ST_SetSRID(ST_MakePoint(3.4716, 6.4474), 4326),
        35000000.00,
        3,
        3,
        NOW(),
        NOW()
    ),
    (
        'Modern 4BR Detached Duplex',
        'Lekki Phase 1, Lagos',
        ST_SetSRID(ST_MakePoint(3.4720, 6.4478), 4326),
        50000000.00,
        4,
        4,
        NOW(),
        NOW()
    );

-- Victoria Island Properties
INSERT INTO properties (title, location_name, location, price, bedrooms, bathrooms, created_at, updated_at)
VALUES 
    (
        'Premium 4BR Penthouse',
        'Victoria Island',
        ST_SetSRID(ST_MakePoint(3.4216, 6.4302), 4326),
        75000000.00,
        4,
        4,
        NOW(),
        NOW()
    ),
    (
        'Corporate 3BR Apartment',
        'VI Extension',
        ST_SetSRID(ST_MakePoint(3.4220, 6.4305), 4326),
        45000000.00,
        3,
        3,
        NOW(),
        NOW()
    );

-- Ikeja Properties
INSERT INTO properties (title, location_name, location, price, bedrooms, bathrooms, created_at, updated_at)
VALUES 
    (
        'Spacious 3BR Flat',
        'Ikeja GRA',
        ST_SetSRID(ST_MakePoint(3.3569, 6.6018), 4326),
        25000000.00,
        3,
        2,
        NOW(),
        NOW()
    ),
    (
        'Executive 4BR Semi-Detached',
        'Ikeja',
        ST_SetSRID(ST_MakePoint(3.3575, 6.6022), 4326),
        35000000.00,
        4,
        3,
        NOW(),
        NOW()
    );

-- Ajah Properties
INSERT INTO properties (title, location_name, location, price, bedrooms, bathrooms, created_at, updated_at)
VALUES 
    (
        'Affordable 2BR Flat',
        'Ajah',
        ST_SetSRID(ST_MakePoint(3.5833, 6.4667), 4326),
        8000000.00,
        2,
        2,
        NOW(),
        NOW()
    ),
    (
        'New 3BR Terrace',
        'Ajah, Lekki',
        ST_SetSRID(ST_MakePoint(3.5840, 6.4670), 4326),
        18000000.00,
        3,
        3,
        NOW(),
        NOW()
    );

-- Yaba Properties
INSERT INTO properties (title, location_name, location, price, bedrooms, bathrooms, created_at, updated_at)
VALUES 
    (
        'Student-Friendly 2BR Apartment',
        'Yaba',
        ST_SetSRID(ST_MakePoint(3.3792, 6.5244), 4326),
        12000000.00,
        2,
        2,
        NOW(),
        NOW()
    ),
    (
        'Modern 3BR Flat',
        'Yaba Lagos',
        ST_SetSRID(ST_MakePoint(3.3795, 6.5248), 4326),
        15000000.00,
        3,
        2,
        NOW(),
        NOW()
    );

-- Ikoyi Properties
INSERT INTO properties (title, location_name, location, price, bedrooms, bathrooms, created_at, updated_at)
VALUES 
    (
        'Ultra-Luxury 5BR Mansion',
        'Ikoyi',
        ST_SetSRID(ST_MakePoint(3.4395, 6.4541), 4326),
        150000000.00,
        5,
        5,
        NOW(),
        NOW()
    ),
    (
        'Exquisite 4BR Penthouse',
        'Old Ikoyi',
        ST_SetSRID(ST_MakePoint(3.4400, 6.4545), 4326),
        95000000.00,
        4,
        4,
        NOW(),
        NOW()
    );

-- Surulere Properties
INSERT INTO properties (title, location_name, location, price, bedrooms, bathrooms, created_at, updated_at)
VALUES 
    (
        'Classic 3BR Bungalow',
        'Surulere',
        ST_SetSRID(ST_MakePoint(3.3561, 6.4969), 4326),
        22000000.00,
        3,
        2,
        NOW(),
        NOW()
    ),
    (
        'Renovated 2BR Flat',
        'Surulere Lagos',
        ST_SetSRID(ST_MakePoint(3.3565, 6.4972), 4326),
        16000000.00,
        2,
        2,
        NOW(),
        NOW()
    );

-- Festac Properties
INSERT INTO properties (title, location_name, location, price, bedrooms, bathrooms, created_at, updated_at)
VALUES 
    (
        'Family 4BR Duplex',
        'Festac Town',
        ST_SetSRID(ST_MakePoint(3.2813, 6.4665), 4326),
        28000000.00,
        4,
        3,
        NOW(),
        NOW()
    ),
    (
        'Comfortable 3BR Flat',
        'Festac',
        ST_SetSRID(ST_MakePoint(3.2820, 6.4670), 4326),
        20000000.00,
        3,
        2,
        NOW(),
        NOW()
    );

-- Verification queries
-- Check total properties inserted
SELECT COUNT(*) as total_properties FROM properties;

-- Check Sangotedo properties (should be at least 4)
SELECT COUNT(*) as sangotedo_properties 
FROM properties 
WHERE location_name ILIKE '%sangotedo%';

-- Display all properties with their coordinates
SELECT 
    id,
    title,
    location_name,
    ST_Y(location::geometry) as latitude,
    ST_X(location::geometry) as longitude,
    price,
    bedrooms,
    bathrooms
FROM properties
ORDER BY location_name, created_at;
