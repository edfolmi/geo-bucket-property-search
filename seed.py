"""
Seed script for Property Search System
Run with: python manage.py shell < seed.py
"""

import os
import django

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'property_search.settings')
django.setup()

from django.contrib.gis.geos import Point
from properties.models import Property, GeoBucket
from properties.services.bucket_service import BucketService

print("Starting database seed...")
print("=" * 60)

# Clear existing data
print("\n1. Clearing existing data...")
Property.objects.all().delete()
GeoBucket.objects.all().delete()
print("✓ Database cleared")

# Sample properties with Sangotedo variations (REQUIRED TEST CASE)
print("\n2. Creating Sangotedo properties (required test case)...")

sangotedo_properties = [
    {
        "title": "Modern 3BR Apartment in Sangotedo",
        "location_name": "Sangotedo",
        "lat": 6.4698,
        "lng": 3.6285,
        "price": 15000000.00,
        "bedrooms": 3,
        "bathrooms": 2
    },
    {
        "title": "Luxury 4BR Duplex",
        "location_name": "Sangotedo, Ajah",
        "lat": 6.4720,
        "lng": 3.6301,
        "price": 25000000.00,
        "bedrooms": 4,
        "bathrooms": 3
    },
    {
        "title": "Cozy 2BR Flat",
        "location_name": "sangotedo lagos",
        "lat": 6.4705,
        "lng": 3.6290,
        "price": 12000000.00,
        "bedrooms": 2,
        "bathrooms": 2
    },
    {
        "title": "Executive 5BR Mansion",
        "location_name": "Sangotedo Lekki",
        "lat": 6.4710,
        "lng": 3.6295,
        "price": 45000000.00,
        "bedrooms": 5,
        "bathrooms": 4
    }
]

for prop_data in sangotedo_properties:
    lat = prop_data.pop('lat')
    lng = prop_data.pop('lng')
    location_name = prop_data['location_name']
    
    # Create point
    point = Point(lng, lat, srid=4326)
    
    # Find or create bucket
    bucket = BucketService.find_or_create_bucket(
        lat=lat,
        lng=lng,
        location_name=location_name
    )
    
    # Create property
    prop = Property.objects.create(
        location=point,
        bucket=bucket,
        **prop_data
    )
    print(f"  ✓ Created: {prop.title} in {location_name}")

print(f"\n✓ Created {len(sangotedo_properties)} Sangotedo properties")

# Additional locations
print("\n3. Creating properties in other locations...")

other_properties = [
    # Lekki Phase 1
    {
        "title": "Luxury 3BR Waterfront Apartment",
        "location_name": "Lekki Phase 1",
        "lat": 6.4474,
        "lng": 3.4716,
        "price": 35000000.00,
        "bedrooms": 3,
        "bathrooms": 3
    },
    {
        "title": "Modern 4BR Detached Duplex",
        "location_name": "Lekki Phase 1, Lagos",
        "lat": 6.4478,
        "lng": 3.4720,
        "price": 50000000.00,
        "bedrooms": 4,
        "bathrooms": 4
    },
    # Victoria Island
    {
        "title": "Premium 4BR Penthouse",
        "location_name": "Victoria Island",
        "lat": 6.4302,
        "lng": 3.4216,
        "price": 75000000.00,
        "bedrooms": 4,
        "bathrooms": 4
    },
    {
        "title": "Corporate 3BR Apartment",
        "location_name": "VI Extension",
        "lat": 6.4305,
        "lng": 3.4220,
        "price": 45000000.00,
        "bedrooms": 3,
        "bathrooms": 3
    },
    # Ikeja
    {
        "title": "Spacious 3BR Flat",
        "location_name": "Ikeja GRA",
        "lat": 6.6018,
        "lng": 3.3569,
        "price": 25000000.00,
        "bedrooms": 3,
        "bathrooms": 2
    },
    {
        "title": "Executive 4BR Semi-Detached",
        "location_name": "Ikeja",
        "lat": 6.6022,
        "lng": 3.3575,
        "price": 35000000.00,
        "bedrooms": 4,
        "bathrooms": 3
    },
    # Ajah
    {
        "title": "Affordable 2BR Flat",
        "location_name": "Ajah",
        "lat": 6.4667,
        "lng": 3.5833,
        "price": 8000000.00,
        "bedrooms": 2,
        "bathrooms": 2
    },
    {
        "title": "New 3BR Terrace",
        "location_name": "Ajah, Lekki",
        "lat": 6.4670,
        "lng": 3.5840,
        "price": 18000000.00,
        "bedrooms": 3,
        "bathrooms": 3
    },
    # Yaba
    {
        "title": "Student-Friendly 2BR Apartment",
        "location_name": "Yaba",
        "lat": 6.5244,
        "lng": 3.3792,
        "price": 12000000.00,
        "bedrooms": 2,
        "bathrooms": 2
    },
    {
        "title": "Modern 3BR Flat",
        "location_name": "Yaba Lagos",
        "lat": 6.5248,
        "lng": 3.3795,
        "price": 15000000.00,
        "bedrooms": 3,
        "bathrooms": 2
    },
    # Ikoyi
    {
        "title": "Ultra-Luxury 5BR Mansion",
        "location_name": "Ikoyi",
        "lat": 6.4541,
        "lng": 3.4395,
        "price": 150000000.00,
        "bedrooms": 5,
        "bathrooms": 5
    },
    {
        "title": "Exquisite 4BR Penthouse",
        "location_name": "Old Ikoyi",
        "lat": 6.4545,
        "lng": 3.4400,
        "price": 95000000.00,
        "bedrooms": 4,
        "bathrooms": 4
    },
    # Surulere
    {
        "title": "Classic 3BR Bungalow",
        "location_name": "Surulere",
        "lat": 6.4969,
        "lng": 3.3561,
        "price": 22000000.00,
        "bedrooms": 3,
        "bathrooms": 2
    },
    {
        "title": "Renovated 2BR Flat",
        "location_name": "Surulere Lagos",
        "lat": 6.4972,
        "lng": 3.3565,
        "price": 16000000.00,
        "bedrooms": 2,
        "bathrooms": 2
    },
    # Festac
    {
        "title": "Family 4BR Duplex",
        "location_name": "Festac Town",
        "lat": 6.4665,
        "lng": 3.2813,
        "price": 28000000.00,
        "bedrooms": 4,
        "bathrooms": 3
    },
    {
        "title": "Comfortable 3BR Flat",
        "location_name": "Festac",
        "lat": 6.4670,
        "lng": 3.2820,
        "price": 20000000.00,
        "bedrooms": 3,
        "bathrooms": 2
    }
]

for prop_data in other_properties:
    lat = prop_data.pop('lat')
    lng = prop_data.pop('lng')
    location_name = prop_data['location_name']
    
    # Create point
    point = Point(lng, lat, srid=4326)
    
    # Find or create bucket
    bucket = BucketService.find_or_create_bucket(
        lat=lat,
        lng=lng,
        location_name=location_name
    )
    
    # Create property
    prop = Property.objects.create(
        location=point,
        bucket=bucket,
        **prop_data
    )
    print(f"  ✓ Created: {prop.title} in {location_name}")

print(f"\n✓ Created {len(other_properties)} additional properties")

# Display statistics
print("\n4. Database Statistics:")
print("=" * 60)

total_properties = Property.objects.count()
total_buckets = GeoBucket.objects.count()
sangotedo_count = Property.objects.filter(
    location_name__icontains='sangotedo'
).count()

print(f"Total Properties: {total_properties}")
print(f"Total Geo-Buckets: {total_buckets}")
print(f"Sangotedo Properties: {sangotedo_count}")

# Display bucket stats
stats = BucketService.get_bucket_stats()
print(f"\nBucket Statistics:")
print(f"  - Buckets with properties: {stats['buckets_with_properties']}")
print(f"  - Empty buckets: {stats['empty_buckets']}")
print(f"  - Avg properties per bucket: {stats['avg_properties_per_bucket']}")
print(f"  - Max properties in a bucket: {stats['max_properties_in_bucket']}")

# Display location distribution
print("\n5. Properties by Location:")
print("=" * 60)

from django.db.models import Count
location_counts = Property.objects.values('bucket__normalized_name').annotate(
    count=Count('id')
).order_by('-count')

for item in location_counts:
    location = item['bucket__normalized_name'] or 'No Bucket'
    count = item['count']
    print(f"  {location}: {count} properties")

print("\n" + "=" * 60)
print("✓ Seed completed successfully!")
print("=" * 60)

print("\nNext steps:")
print("1. Run the server: python manage.py runserver")
print("2. Test the API:")
print("   GET  http://localhost:8000/api/properties/")
print("   GET  http://localhost:8000/api/properties/search?location=sangotedo")
print("   POST http://localhost:8000/api/properties/")
print("   GET  http://localhost:8000/api/geo-buckets/stats/")
print("\n" + "=" * 60)