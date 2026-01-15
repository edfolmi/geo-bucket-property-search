import pytest
from django.contrib.gis.geos import Point
from properties.models import Property, GeoBucket
from properties.services.bucket_service import BucketService
from properties.services.location_matcher import LocationMatcher
from properties.services.normalization import LocationNormalizer


@pytest.mark.django_db
class TestLocationMatching:
    """Test location matching and normalization functionality."""
    
    def test_required_case_sangotedo_variations(self):
        """
        REQUIRED TEST: All Sangotedo variations should return all properties.
        
        This is the core requirement from the assessment:
        - Create 3 properties with different Sangotedo variations
        - Search for "sangotedo" should return all 3
        """
        # Create properties with different location name variations
        prop1 = Property.objects.create(
            title="Modern 3BR Apartment",
            location_name="Sangotedo",
            location=Point(3.6285, 6.4698, srid=4326),
            price=15000000,
            bedrooms=3,
            bathrooms=2
        )
        
        prop2 = Property.objects.create(
            title="Luxury Duplex",
            location_name="Sangotedo, Ajah",
            location=Point(3.6301, 6.4720, srid=4326),
            price=25000000,
            bedrooms=4,
            bathrooms=3
        )
        
        prop3 = Property.objects.create(
            title="Cozy 2BR Flat",
            location_name="sangotedo lagos",
            location=Point(3.6290, 6.4705, srid=4326),
            price=12000000,
            bedrooms=2,
            bathrooms=2
        )
        
        # Assign buckets (should happen in serializer, but doing manually for test)
        for prop in [prop1, prop2, prop3]:
            bucket = BucketService.find_or_create_bucket(
                lat=prop.location.y,
                lng=prop.location.x,
                location_name=prop.location_name
            )
            prop.bucket = bucket
            prop.save()
        
        # Search for "sangotedo" - should return all 3 properties
        matching_buckets = LocationMatcher.find_matching_buckets(
            search_term="sangotedo",
            lat=6.47,
            lng=3.63
        )
        
        # Get all properties from matched buckets
        bucket_ids = [b.id for b in matching_buckets]
        found_properties = Property.objects.filter(bucket_id__in=bucket_ids)
        
        # Assertions
        assert found_properties.count() == 3, \
            f"Expected 3 properties, found {found_properties.count()}"
        
        property_ids = set(found_properties.values_list('id', flat=True))
        assert prop1.id in property_ids
        assert prop2.id in property_ids
        assert prop3.id in property_ids
    
    def test_case_insensitive_matching(self):
        """Test that location matching is case-insensitive."""
        # Create property
        prop = Property.objects.create(
            title="Test Property",
            location_name="Lekki Phase 1",
            location=Point(3.4716, 6.4474, srid=4326),
            price=20000000,
            bedrooms=3,
            bathrooms=2
        )
        
        bucket = BucketService.find_or_create_bucket(
            lat=6.4474,
            lng=3.4716,
            location_name="Lekki Phase 1"
        )
        prop.bucket = bucket
        prop.save()
        
        # Test various case combinations
        for search_term in ["lekki", "LEKKI", "Lekki", "LeKkI"]:
            buckets = LocationMatcher.find_matching_buckets(
                search_term=search_term,
                lat=6.4474,
                lng=3.4716
            )
            assert len(buckets) > 0, f"No buckets found for '{search_term}'"
    
    def test_fuzzy_typo_tolerance(self):
        """Test that search handles typos in location names."""
        # Create property
        prop = Property.objects.create(
            title="Beach House",
            location_name="Ajah",
            location=Point(3.5833, 6.4667, srid=4326),
            price=30000000,
            bedrooms=4,
            bathrooms=3
        )
        
        bucket = BucketService.find_or_create_bucket(
            lat=6.4667,
            lng=3.5833,
            location_name="Ajah"
        )
        prop.bucket = bucket
        prop.save()
        
        # Test typos (Levenshtein distance <= 2)
        typo_searches = ["ajah", "aja", "ajsh"]
        
        for search in typo_searches:
            buckets = LocationMatcher.find_matching_buckets(
                search_term=search,
                lat=6.4667,
                lng=3.5833
            )
            # Should find the bucket despite typo
            assert len(buckets) > 0, f"No buckets found for typo '{search}'"
    
    def test_spatial_proximity_grouping(self):
        """Test that nearby properties are grouped in same bucket."""
        # Create two properties very close to each other
        prop1 = Property.objects.create(
            title="Property 1",
            location_name="VI Extension",
            location=Point(3.4216, 6.4302, srid=4326),
            price=40000000,
            bedrooms=3,
            bathrooms=2
        )
        
        # Second property 50m away (within same H3 cell)
        prop2 = Property.objects.create(
            title="Property 2",
            location_name="Victoria Island",
            location=Point(3.4220, 6.4305, srid=4326),
            price=45000000,
            bedrooms=4,
            bathrooms=3
        )
        
        # Assign buckets
        bucket1 = BucketService.find_or_create_bucket(
            lat=6.4302,
            lng=3.4216,
            location_name="VI Extension"
        )
        bucket2 = BucketService.find_or_create_bucket(
            lat=6.4305,
            lng=3.4220,
            location_name="Victoria Island"
        )
        
        prop1.bucket = bucket1
        prop2.bucket = bucket2
        prop1.save()
        prop2.save()
        
        # Properties should be in same or neighboring buckets
        # due to proximity
        h3_1 = BucketService.calculate_h3_index(6.4302, 3.4216)
        h3_2 = BucketService.calculate_h3_index(6.4305, 3.4220)
        
        # Either same cell or neighbors
        neighbors_1 = BucketService.get_h3_neighbors(h3_1)
        assert h3_2 in neighbors_1 or h3_1 == h3_2
    
    def test_location_name_normalization(self):
        """Test location name normalization removes noise."""
        test_cases = [
            ("Sangotedo, Ajah", "sangotedo ajah"),
            ("sangotedo lagos", "sangotedo"),
            ("Sangotedo", "sangotedo"),
            ("Lekki Phase 1, Lagos State", "lekki phase 1"),
            ("Ikoyi - Lagos", "ikoyi"),
        ]
        
        for input_name, expected_output in test_cases:
            normalized = LocationNormalizer.normalize(input_name)
            assert normalized == expected_output, \
                f"Expected '{expected_output}', got '{normalized}'"
    
    def test_h3_index_calculation(self):
        """Test H3 index calculation is consistent."""
        lat, lng = 6.4698, 3.6285
        
        # Calculate twice
        h3_1 = BucketService.calculate_h3_index(lat, lng)
        h3_2 = BucketService.calculate_h3_index(lat, lng)
        
        # Should be identical
        assert h3_1 == h3_2
        
        # Should be valid H3 index
        assert len(h3_1) == 15
        assert h3_1.startswith('89')  # Resolution 9 prefix
    
    def test_multiple_properties_same_bucket(self):
        """Test that multiple properties can be in same bucket."""
        # Create 5 properties in same location
        for i in range(5):
            prop = Property.objects.create(
                title=f"Property {i+1}",
                location_name="Ikeja",
                location=Point(3.3569, 6.6018, srid=4326),
                price=15000000 + (i * 1000000),
                bedrooms=3,
                bathrooms=2
            )
            
            bucket = BucketService.find_or_create_bucket(
                lat=6.6018,
                lng=3.3569,
                location_name="Ikeja"
            )
            prop.bucket = bucket
            prop.save()
        
        # Should all be in same bucket
        buckets = GeoBucket.objects.filter(
            properties__location_name="Ikeja"
        ).distinct()
        
        assert buckets.count() == 1
        bucket = buckets.first()
        assert bucket.property_count == 5
    
    def test_empty_search_returns_empty(self):
        """Test that empty search term returns no results."""
        buckets = LocationMatcher.find_matching_buckets(search_term="")
        assert len(buckets) == 0
    
    def test_nonexistent_location_returns_empty(self):
        """Test that search for nonexistent location returns empty."""
        buckets = LocationMatcher.find_matching_buckets(
            search_term="NonexistentLocation123",
            lat=0,
            lng=0
        )
        assert len(buckets) == 0


@pytest.mark.django_db
class TestBucketService:
    """Test bucket service functionality."""
    
    def test_create_new_bucket(self):
        """Test creating a new bucket."""
        bucket = BucketService.find_or_create_bucket(
            lat=6.5244,
            lng=3.3792,
            location_name="Yaba"
        )
        
        assert bucket is not None
        assert bucket.normalized_name == "yaba"
        assert "Yaba" in bucket.variant_names
        assert bucket.property_count == 0
    
    def test_find_existing_bucket(self):
        """Test finding an existing bucket."""
        # Create first bucket
        bucket1 = BucketService.find_or_create_bucket(
            lat=6.4302,
            lng=3.4216,
            location_name="VI"
        )
        
        # Try to create again with same coordinates
        bucket2 = BucketService.find_or_create_bucket(
            lat=6.4302,
            lng=3.4216,
            location_name="Victoria Island"
        )
        
        # Should return same bucket
        assert bucket1.id == bucket2.id
        
        # Should add new variant
        assert "VI" in bucket2.variant_names
        assert "Victoria Island" in bucket2.variant_names
    
    def test_bucket_stats_calculation(self):
        """Test bucket statistics calculation."""
        # Create some test data
        for i in range(3):
            bucket = BucketService.find_or_create_bucket(
                lat=6.5 + (i * 0.01),
                lng=3.3 + (i * 0.01),
                location_name=f"Location {i}"
            )
            
            # Create properties for each bucket
            for j in range(i + 1):
                Property.objects.create(
                    title=f"Property {j}",
                    location_name=f"Location {i}",
                    location=Point(3.3 + (i * 0.01), 6.5 + (i * 0.01), srid=4326),
                    bucket=bucket,
                    price=10000000,
                    bedrooms=2,
                    bathrooms=1
                )
                bucket.increment_property_count()
        
        # Get stats
        stats = BucketService.get_bucket_stats()
        
        assert stats['total_buckets'] == 3
        assert stats['total_properties'] == 6  # 1 + 2 + 3
        assert stats['buckets_with_properties'] == 3
