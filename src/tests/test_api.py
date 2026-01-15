import pytest
from rest_framework.test import APIClient
from rest_framework import status
from django.contrib.gis.geos import Point
from properties.models import Property, GeoBucket
from properties.services.bucket_service import BucketService


@pytest.fixture
def api_client():
    """Fixture for DRF API client."""
    return APIClient()


@pytest.mark.django_db
class TestPropertyAPI:
    """Test Property API endpoints."""
    
    def test_create_property(self, api_client):
        """Test POST /api/properties/ creates property with bucket."""
        data = {
            "title": "3 Bedroom Flat in Sangotedo",
            "location_name": "Sangotedo",
            "lat": 6.4698,
            "lng": 3.6285,
            "price": "15000000.00",
            "bedrooms": 3,
            "bathrooms": 2
        }
        
        response = api_client.post(
            '/api/properties/',
            data=data,
            format='json'
        )
        
        assert response.status_code == status.HTTP_201_CREATED
        assert response.data['title'] == "3 Bedroom Flat in Sangotedo"
        assert response.data['bucket_name'] == "sangotedo"
        assert 'bucket_h3_index' in response.data
        
        # Verify property was created
        prop = Property.objects.get(id=response.data['id'])
        assert prop.title == data['title']
        assert prop.bucket is not None
    
    def test_create_property_invalid_coordinates(self, api_client):
        """Test creating property with invalid coordinates fails."""
        data = {
            "title": "Invalid Property",
            "location_name": "Test",
            "lat": 200,  # Invalid latitude
            "lng": 3.0,
            "price": "10000000",
            "bedrooms": 2,
            "bathrooms": 1
        }
        
        response = api_client.post(
            '/api/properties/',
            data=data,
            format='json'
        )
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert 'lat' in response.data
    
    def test_list_properties(self, api_client):
        """Test GET /api/properties/ lists all properties."""
        # Create test properties
        for i in range(3):
            Property.objects.create(
                title=f"Property {i}",
                location_name="Test Location",
                location=Point(3.5 + i*0.01, 6.5 + i*0.01, srid=4326),
                price=10000000,
                bedrooms=2,
                bathrooms=1
            )
        
        response = api_client.get('/api/properties/')
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['count'] == 3
        assert len(response.data['results']) == 3
    
    def test_search_properties_by_location(self, api_client):
        """Test GET /api/properties/search/?location=X returns properties."""
        # Create properties with Sangotedo variations
        locations = [
            ("Sangotedo", 6.4698, 3.6285),
            ("Sangotedo, Ajah", 6.4720, 3.6301),
            ("sangotedo lagos", 6.4705, 3.6290)
        ]
        
        for location_name, lat, lng in locations:
            prop = Property.objects.create(
                title=f"Property in {location_name}",
                location_name=location_name,
                location=Point(lng, lat, srid=4326),
                price=15000000,
                bedrooms=3,
                bathrooms=2
            )
            # Assign bucket
            bucket = BucketService.find_or_create_bucket(
                lat=lat,
                lng=lng,
                location_name=location_name
            )
            prop.bucket = bucket
            prop.save()
        
        # Search for "sangotedo"
        response = api_client.get('/api/properties/search/?location=sangotedo')
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['count'] == 3
        assert 'search_term' in response.data
        assert 'matched_buckets' in response.data
        assert len(response.data['results']) == 3
    
    def test_search_without_location_parameter(self, api_client):
        """Test search endpoint requires location parameter."""
        response = api_client.get('/api/properties/search/')
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert 'location' in response.data
    
    def test_search_nonexistent_location(self, api_client):
        """Test search for nonexistent location returns empty."""
        response = api_client.get(
            '/api/properties/search/?location=NonexistentLocation123'
        )
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['count'] == 0
        assert len(response.data['results']) == 0
    
    def test_search_with_coordinates(self, api_client):
        """Test search with lat/lng parameters."""
        # Create property
        prop = Property.objects.create(
            title="Test Property",
            location_name="Lekki",
            location=Point(3.4716, 6.4474, srid=4326),
            price=20000000,
            bedrooms=3,
            bathrooms=2
        )
        bucket = BucketService.find_or_create_bucket(
            lat=6.4474,
            lng=3.4716,
            location_name="Lekki"
        )
        prop.bucket = bucket
        prop.save()
        
        # Search with coordinates
        response = api_client.get(
            '/api/properties/search/?location=lekki&lat=6.4474&lng=3.4716'
        )
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['count'] >= 1
    
    def test_update_property(self, api_client):
        """Test PUT /api/properties/{id}/ updates property."""
        # Create property
        prop = Property.objects.create(
            title="Original Title",
            location_name="Original Location",
            location=Point(3.5, 6.5, srid=4326),
            price=10000000,
            bedrooms=2,
            bathrooms=1
        )
        
        # Update property
        updated_data = {
            "title": "Updated Title",
            "location_name": "Updated Location",
            "lat": 6.5,
            "lng": 3.5,
            "price": "12000000",
            "bedrooms": 3,
            "bathrooms": 2
        }
        
        response = api_client.put(
            f'/api/properties/{prop.id}/',
            data=updated_data,
            format='json'
        )
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['title'] == "Updated Title"
        
        # Verify update
        prop.refresh_from_db()
        assert prop.title == "Updated Title"
        assert prop.bedrooms == 3
    
    def test_delete_property(self, api_client):
        """Test DELETE /api/properties/{id}/ deletes property."""
        # Create property
        prop = Property.objects.create(
            title="To Delete",
            location_name="Test",
            location=Point(3.5, 6.5, srid=4326),
            price=10000000,
            bedrooms=2,
            bathrooms=1
        )
        
        prop_id = prop.id
        
        # Delete property
        response = api_client.delete(f'/api/properties/{prop_id}/')
        
        assert response.status_code == status.HTTP_204_NO_CONTENT
        
        # Verify deletion
        assert not Property.objects.filter(id=prop_id).exists()


@pytest.mark.django_db
class TestGeoBucketAPI:
    """Test GeoBucket API endpoints."""
    
    def test_list_buckets(self, api_client):
        """Test GET /api/geo-buckets/ lists all buckets."""
        # Create test buckets
        for i in range(3):
            BucketService.find_or_create_bucket(
                lat=6.5 + i*0.01,
                lng=3.3 + i*0.01,
                location_name=f"Location {i}"
            )
        
        response = api_client.get('/api/geo-buckets/')
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['count'] == 3
    
    def test_get_bucket_stats(self, api_client):
        """Test GET /api/geo-buckets/stats/ returns statistics."""
        # Create test data
        bucket = BucketService.find_or_create_bucket(
            lat=6.5,
            lng=3.3,
            location_name="Test Location"
        )
        
        # Create properties
        for i in range(5):
            prop = Property.objects.create(
                title=f"Property {i}",
                location_name="Test Location",
                location=Point(3.3, 6.5, srid=4326),
                bucket=bucket,
                price=10000000,
                bedrooms=2,
                bathrooms=1
            )
            bucket.increment_property_count()
        
        response = api_client.get('/api/geo-buckets/stats/')
        
        assert response.status_code == status.HTTP_200_OK
        assert 'total_buckets' in response.data
        assert 'total_properties' in response.data
        assert response.data['total_buckets'] >= 1
        assert response.data['total_properties'] >= 5
    
    def test_get_bucket_stats_with_details(self, api_client):
        """Test bucket stats endpoint with details parameter."""
        BucketService.find_or_create_bucket(
            lat=6.5,
            lng=3.3,
            location_name="Test"
        )
        
        response = api_client.get('/api/geo-buckets/stats/?details=true')
        
        assert response.status_code == status.HTTP_200_OK
        assert 'bucket_details' in response.data
        assert len(response.data['bucket_details']) >= 1
    
    def test_get_specific_bucket(self, api_client):
        """Test GET /api/geo-buckets/{id}/ returns bucket details."""
        bucket = BucketService.find_or_create_bucket(
            lat=6.5,
            lng=3.3,
            location_name="Test Location"
        )
        
        response = api_client.get(f'/api/geo-buckets/{bucket.id}/')
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['id'] == bucket.id
        assert response.data['normalized_name'] == bucket.normalized_name
        assert 'h3_index' in response.data
        assert 'centroid_lat' in response.data
        assert 'centroid_lng' in response.data
