from rest_framework import serializers
from django.contrib.gis.geos import Point
from properties.models import Property, GeoBucket
from properties.services.bucket_service import BucketService


class PropertySerializer(serializers.ModelSerializer):
    """Serializer for Property model with automatic bucket assignment."""
    
    lat = serializers.FloatField(write_only=True)
    lng = serializers.FloatField(write_only=True)
    
    latitude = serializers.FloatField(source='location.y', read_only=True)
    longitude = serializers.FloatField(source='location.x', read_only=True)
    
    bucket_name = serializers.CharField(
        source='bucket.normalized_name',
        read_only=True,
        allow_null=True
    )
    bucket_h3_index = serializers.CharField(
        source='bucket.h3_index',
        read_only=True,
        allow_null=True
    )
    
    class Meta:
        model = Property
        fields = [
            'id',
            'title',
            'location_name',
            'lat',
            'lng',
            'latitude',
            'longitude',
            'bucket_name',
            'bucket_h3_index',
            'price',
            'bedrooms',
            'bathrooms',
            'created_at',
            'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']

    def validate(self, data):
        """Validate coordinates are within reasonable bounds."""
        lat = data.get('lat')
        lng = data.get('lng')
        
        if lat is not None and (lat < -90 or lat > 90):
            raise serializers.ValidationError({
                'lat': 'Latitude must be between -90 and 90'
            })
        
        if lng is not None and (lng < -180 or lng > 180):
            raise serializers.ValidationError({
                'lng': 'Longitude must be between -180 and 180'
            })
        
        return data

    def create(self, validated_data):
        """Create property with automatic bucket assignment."""
        lat = validated_data.pop('lat')
        lng = validated_data.pop('lng')
        location_name = validated_data.get('location_name')
        
        # Create Point geometry
        point = Point(lng, lat, srid=4326)
        validated_data['location'] = point
        
        # Find or create appropriate bucket
        bucket = BucketService.find_or_create_bucket(
            lat=lat,
            lng=lng,
            location_name=location_name
        )
        validated_data['bucket'] = bucket
        
        # Create property
        property_instance = Property.objects.create(**validated_data)
        
        return property_instance

    def update(self, instance, validated_data):
        """Update property and reassign bucket if location changed."""
        lat = validated_data.pop('lat', None)
        lng = validated_data.pop('lng', None)
        
        # Update location if coordinates provided
        if lat is not None and lng is not None:
            point = Point(lng, lat, srid=4326)
            instance.location = point
            
            # Reassign bucket
            location_name = validated_data.get(
                'location_name',
                instance.location_name
            )
            bucket = BucketService.find_or_create_bucket(
                lat=lat,
                lng=lng,
                location_name=location_name
            )
            instance.bucket = bucket
        
        # Update other fields
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        
        instance.save()
        return instance


class PropertySearchSerializer(serializers.Serializer):
    """Serializer for property search results."""
    
    id = serializers.IntegerField()
    title = serializers.CharField()
    location_name = serializers.CharField()
    latitude = serializers.FloatField()
    longitude = serializers.FloatField()
    bucket_name = serializers.CharField(allow_null=True)
    price = serializers.DecimalField(max_digits=12, decimal_places=2)
    bedrooms = serializers.IntegerField()
    bathrooms = serializers.IntegerField()
    created_at = serializers.DateTimeField()


class GeoBucketSerializer(serializers.ModelSerializer):
    """Serializer for GeoBucket model."""
    
    centroid_lat = serializers.FloatField(source='centroid.y', read_only=True)
    centroid_lng = serializers.FloatField(source='centroid.x', read_only=True)
    
    class Meta:
        model = GeoBucket
        fields = [
            'id',
            'h3_index',
            'centroid_lat',
            'centroid_lng',
            'normalized_name',
            'variant_names',
            'property_count',
            'created_at',
            'updated_at'
        ]
        read_only_fields = fields


class BucketStatsSerializer(serializers.Serializer):
    """Serializer for bucket statistics."""
    
    total_buckets = serializers.IntegerField()
    total_properties = serializers.IntegerField()
    avg_properties_per_bucket = serializers.FloatField()
    max_properties_in_bucket = serializers.IntegerField()
    min_properties_in_bucket = serializers.IntegerField()
    buckets_with_properties = serializers.IntegerField()
    empty_buckets = serializers.IntegerField()
    bucket_details = GeoBucketSerializer(many=True, required=False)