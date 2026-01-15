from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.exceptions import ValidationError
from django.db.models import Q
from properties.models import Property, GeoBucket
from properties.serializers import (
    PropertySerializer,
    PropertySearchSerializer,
    BucketStatsSerializer,
    GeoBucketSerializer
)
from properties.services.location_matcher import LocationMatcher
from properties.services.bucket_service import BucketService


# Create your views here.
class PropertyViewSet(viewsets.ModelViewSet):
    """
    ViewSet for Property CRUD operations and location-based search.
    
    Endpoints:
    - POST /api/properties/ - Create property with auto bucket assignment
    - GET /api/properties/ - List all properties
    - GET /api/properties/{id}/ - Get specific property
    - PUT/PATCH /api/properties/{id}/ - Update property
    - DELETE /api/properties/{id}/ - Delete property
    - GET /api/properties/search/?location=<name> - Search by location
    """
    
    queryset = Property.objects.select_related('bucket').all()
    serializer_class = PropertySerializer

    def create(self, request, *args, **kwargs):
        """
        Create a new property with automatic bucket assignment.
        
        Request body:
        {
            "title": "3 Bedroom Flat",
            "location_name": "Sangotedo",
            "lat": 6.4698,
            "lng": 3.6285,
            "price": 15000000,
            "bedrooms": 3,
            "bathrooms": 2
        }
        """
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        
        headers = self.get_success_headers(serializer.data)
        return Response(
            serializer.data,
            status=status.HTTP_201_CREATED,
            headers=headers
        )

    @action(detail=False, methods=['get'], url_path='search')
    def search(self, request):
        """
        Search for properties by location name.
        
        Query parameters:
        - location (required): Location name to search for
        - lat (optional): Latitude for spatial search
        - lng (optional): Longitude for spatial search
        
        Example:
        GET /api/properties/search?location=sangotedo
        GET /api/properties/search?location=sangotedo&lat=6.47&lng=3.63
        
        Returns all properties in matching geo-buckets with:
        - Case-insensitive matching
        - Typo tolerance
        - Location name variant support
        """
        location = request.query_params.get('location')
        
        if not location:
            raise ValidationError({
                'location': 'This query parameter is required'
            })
        
        # Optional coordinates for spatial search
        lat = request.query_params.get('lat')
        lng = request.query_params.get('lng')
        
        # Convert and validate coordinates if provided
        if lat and lng:
            try:
                lat = float(lat)
                lng = float(lng)
                
                # Validate Nigeria bounds
                if not (4.0 <= lat <= 14.0 and 3.0 <= lng <= 15.0):
                    # Log warning but continue with name-only search
                    lat, lng = None, None
                    
            except (ValueError, TypeError):
                # Invalid coordinates - fall back to name-only search
                lat, lng = None, None
        
        # Find matching buckets (works with or without coordinates)
        matching_buckets = LocationMatcher.find_matching_buckets(
            search_term=location,
            lat=lat,
            lng=lng
        )
        
        if not matching_buckets:
            return Response({
                'count': 0,
                'results': [],
                'message': f'No properties found for location: {location}'
            })
        
        # Get all properties in matching buckets
        bucket_ids = [bucket.id for bucket in matching_buckets]
        properties = Property.objects.filter(
            bucket_id__in=bucket_ids
        ).select_related('bucket').order_by('-created_at')
        
        # Serialize results
        results = []
        for prop in properties:
            results.append({
                'id': prop.id,
                'title': prop.title,
                'location_name': prop.location_name,
                'latitude': prop.latitude,
                'longitude': prop.longitude,
                'bucket_name': prop.bucket.normalized_name if prop.bucket else None,
                'price': str(prop.price),
                'bedrooms': prop.bedrooms,
                'bathrooms': prop.bathrooms,
                'created_at': prop.created_at.isoformat()
            })
        
        return Response({
            'count': len(results),
            'search_term': location,
            'matched_buckets': [b.normalized_name for b in matching_buckets],
            'results': results
        })


class GeoBucketViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet for GeoBucket read operations and statistics.
    
    Endpoints:
    - GET /api/geo-buckets/ - List all buckets
    - GET /api/geo-buckets/{id}/ - Get specific bucket
    - GET /api/geo-buckets/stats/ - Get bucket statistics
    """
    
    queryset = GeoBucket.objects.all()
    serializer_class = GeoBucketSerializer

    @action(detail=False, methods=['get'], url_path='stats')
    def stats(self, request):
        """
        Get statistics about geo-buckets.
        
        Returns:
        {
            "total_buckets": 50,
            "total_properties": 147,
            "avg_properties_per_bucket": 2.94,
            "max_properties_in_bucket": 15,
            "min_properties_in_bucket": 0,
            "buckets_with_properties": 45,
            "empty_buckets": 5,
            "bucket_details": [...]  // Optional, include with ?details=true
        }
        """
        stats = BucketService.get_bucket_stats()
        
        # Include detailed bucket info if requested
        include_details = request.query_params.get('details', 'false').lower() == 'true'
        
        if include_details:
            bucket_details = BucketService.get_bucket_details()
            stats['bucket_details'] = bucket_details
        
        serializer = BucketStatsSerializer(stats)
        return Response(serializer.data)
