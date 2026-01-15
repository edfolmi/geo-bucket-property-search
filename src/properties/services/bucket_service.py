import h3
from django.contrib.gis.geos import Point
from typing import Optional, List, Tuple
from properties.models import GeoBucket, LocationIndex
from properties.services.normalization import LocationNormalizer


class BucketService:
    """
    Service for managing geo-buckets and property assignments.
    Uses H3 hexagonal grid system for spatial indexing.
    """
    
    # H3 resolution 9: ~174m diameter hexagons
    H3_RESOLUTION = 9

    @classmethod
    def calculate_h3_index(cls, lat: float, lng: float) -> str:
        """
        Calculate H3 index for given coordinates.
        
        Args:
            lat: Latitude
            lng: Longitude
            
        Returns:
            H3 index string
        """
        return h3.latlng_to_cell(lat, lng, cls.H3_RESOLUTION)

    @classmethod
    def get_h3_neighbors(cls, h3_index: str) -> List[str]:
        """
        Get neighboring H3 cells (ring-1).
        
        Args:
            h3_index: Center H3 index
            
        Returns:
            List of neighboring H3 indices (includes center)
        """
        neighbors = h3.grid_disk(h3_index, 1)
        return list(neighbors)

    @classmethod
    def get_h3_neighbors_extended(cls, h3_index: str) -> List[str]:
        """
        Get extended neighbors (ring-2) for broader search.
        
        Args:
            h3_index: Center H3 index
            
        Returns:
            List of H3 indices within 2-ring distance
        """
        neighbors = h3.grid_disk(h3_index, 2)
        return list(neighbors)

    @classmethod
    def h3_to_coordinates(cls, h3_index: str) -> Tuple[float, float]:
        """
        Convert H3 index to center coordinates.
        
        Args:
            h3_index: H3 index
            
        Returns:
            Tuple of (latitude, longitude)
        """
        lat, lng = h3.cell_to_latlng(h3_index)
        return lat, lng

    @classmethod
    def find_or_create_bucket(
        cls,
        lat: float,
        lng: float,
        location_name: str
    ) -> GeoBucket:
        """
        Find existing bucket or create new one for given location.
        
        Process:
        1. Calculate H3 index from coordinates
        2. Check if bucket exists for this H3 cell
        3. If not, create new bucket
        4. Add location name variant to bucket
        
        Args:
            lat: Latitude
            lng: Longitude
            location_name: Original location name
            
        Returns:
            GeoBucket instance
        """
        h3_index = cls.calculate_h3_index(lat, lng)
        normalized_name = LocationNormalizer.normalize(location_name)
        
        # Try to find existing bucket
        bucket = GeoBucket.objects.filter(h3_index=h3_index).first()
        
        if bucket:
            # Add location name variant if new
            bucket.add_variant_name(location_name)
            
            # Add to location index
            cls._add_to_location_index(bucket, location_name, normalized_name)
            
            return bucket
        
        # Create new bucket
        centroid_lat, centroid_lng = cls.h3_to_coordinates(h3_index)
        centroid = Point(centroid_lng, centroid_lat, srid=4326)
        
        bucket = GeoBucket.objects.create(
            h3_index=h3_index,
            centroid=centroid,
            normalized_name=normalized_name,
            variant_names=[location_name] if location_name else []
        )
        
        # Add to location index
        cls._add_to_location_index(bucket, location_name, normalized_name)
        
        return bucket

    @classmethod
    def _add_to_location_index(
        cls,
        bucket: GeoBucket,
        original_name: str,
        normalized_name: str
    ):
        """
        Add location name to fuzzy matching index.
        
        Args:
            bucket: GeoBucket instance
            original_name: Original location name
            normalized_name: Normalized location name
        """
        # Check if already indexed
        exists = LocationIndex.objects.filter(
            original_name=original_name,
            bucket=bucket
        ).exists()
        
        if exists:
            return
        
        # Generate trigrams and metaphone
        trigrams = LocationNormalizer.generate_trigrams(normalized_name)
        metaphone = LocationNormalizer.metaphone_simple(normalized_name)
        
        LocationIndex.objects.create(
            original_name=original_name,
            normalized_name=normalized_name,
            bucket=bucket,
            metaphone=metaphone,
            trigrams=trigrams
        )

    @classmethod
    def get_bucket_stats(cls) -> dict:
        """
        Calculate statistics about geo-buckets.
        
        Returns:
            Dictionary with bucket statistics
        """
        from django.db.models import Count, Avg, Max, Min
        
        buckets = GeoBucket.objects.all()
        total_buckets = buckets.count()
        
        if total_buckets == 0:
            return {
                'total_buckets': 0,
                'total_properties': 0,
                'avg_properties_per_bucket': 0,
                'max_properties_in_bucket': 0,
                'min_properties_in_bucket': 0,
                'buckets_with_properties': 0,
                'empty_buckets': 0
            }
        
        stats = buckets.aggregate(
            total_properties=Count('properties'),
            avg_properties=Avg('property_count'),
            max_properties=Max('property_count'),
            min_properties=Min('property_count')
        )
        
        buckets_with_properties = buckets.filter(property_count__gt=0).count()
        empty_buckets = total_buckets - buckets_with_properties
        
        return {
            'total_buckets': total_buckets,
            'total_properties': stats['total_properties'] or 0,
            'avg_properties_per_bucket': round(stats['avg_properties'] or 0, 2),
            'max_properties_in_bucket': stats['max_properties'] or 0,
            'min_properties_in_bucket': stats['min_properties'] or 0,
            'buckets_with_properties': buckets_with_properties,
            'empty_buckets': empty_buckets
        }

    @classmethod
    def get_bucket_details(cls) -> List[dict]:
        """
        Get detailed information about all buckets.
        
        Returns:
            List of bucket detail dictionaries
        """
        buckets = GeoBucket.objects.all()
        
        return [
            {
                'id': bucket.id,
                'h3_index': bucket.h3_index,
                'normalized_name': bucket.normalized_name,
                'variant_names': bucket.variant_names,
                'property_count': bucket.property_count,
                'centroid': {
                    'lat': bucket.centroid.y,
                    'lng': bucket.centroid.x
                }
            }
            for bucket in buckets
        ]
