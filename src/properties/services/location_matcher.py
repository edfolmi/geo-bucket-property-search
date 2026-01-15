import Levenshtein
from typing import List, Optional
from django.db.models import Q
from properties.models import GeoBucket, LocationIndex
from properties.services.bucket_service import BucketService
from properties.services.normalization import LocationNormalizer


class LocationMatcher:
    """
    Handles fuzzy location matching for property searches.
    Implements multi-layer matching strategy:
    1. Exact H3 match
    2. Spatial + name match
    3. Fuzzy name matching
    4. Extended spatial search
    """
    
    # Similarity thresholds
    EXACT_MATCH_THRESHOLD = 0.95
    GOOD_MATCH_THRESHOLD = 0.8
    ACCEPTABLE_MATCH_THRESHOLD = 0.6
    
    # Levenshtein distance threshold
    MAX_LEVENSHTEIN_DISTANCE = 2

    @classmethod
    def find_matching_buckets(
        cls,
        search_term: str,
        lat: Optional[float] = None,
        lng: Optional[float] = None,
        min_results: int = 5
    ) -> List[GeoBucket]:
        """
        Enhanced matching with graceful degradation.
        """
        if not search_term:
            return []
        
        normalized_search = LocationNormalizer.normalize(search_term)
        buckets = []
        
        # Layer 1: Exact name match (works without coordinates)
        buckets.extend(cls._exact_name_match(normalized_search))
        
        if len(buckets) >= min_results:
            return cls._deduplicate_buckets(buckets)
        
        # Layer 2: Only if coordinates are VALID and TRUSTED
        if lat is not None and lng is not None and cls._validate_coords(lat, lng):
            spatial_buckets = cls._spatial_name_match(normalized_search, lat, lng)
            buckets.extend(spatial_buckets)
            
            if len(buckets) >= min_results:
                return cls._deduplicate_buckets(buckets)
        
        # Layer 3: Fuzzy name matching (no coordinates needed)
        fuzzy_buckets = cls._fuzzy_name_match(normalized_search)
        buckets.extend(fuzzy_buckets)
        
        return cls._deduplicate_buckets(buckets)

    @classmethod
    def _validate_coords(cls, lat: float, lng: float) -> bool:
        """
        Validate coordinates are reasonable for Nigeria.
        
        Nigeria bounds approximately:
        - Latitude: 4°N to 14°N
        - Longitude: 3°E to 15°E
        """
        if not (4.0 <= lat <= 14.0):
            return False
        if not (3.0 <= lng <= 15.0):
            return False
        return True

    @classmethod
    def _exact_name_match(cls, normalized_name: str) -> List[GeoBucket]:
        """
        Layer 1: Find buckets with exact normalized name match.
        
        Args:
            normalized_name: Normalized search term
            
        Returns:
            List of matching buckets
        """
        return list(GeoBucket.objects.filter(
            normalized_name__iexact=normalized_name
        ))

    @classmethod
    def _spatial_name_match(
        cls,
        normalized_name: str,
        lat: float,
        lng: float
    ) -> List[GeoBucket]:
        """
        Layer 2: Find buckets in spatial proximity with similar names.
        
        Args:
            normalized_name: Normalized search term
            lat: Latitude
            lng: Longitude
            
        Returns:
            List of matching buckets
        """
        # Get H3 cell and neighbors
        h3_index = BucketService.calculate_h3_index(lat, lng)
        neighbor_indices = BucketService.get_h3_neighbors(h3_index)
        
        # Find buckets in these cells with similar names
        buckets = GeoBucket.objects.filter(
            h3_index__in=neighbor_indices
        )
        
        # Filter by name similarity
        matching_buckets = []
        for bucket in buckets:
            if cls._is_name_match(normalized_name, bucket.normalized_name):
                matching_buckets.append(bucket)
            elif cls._check_variant_names(normalized_name, bucket.variant_names):
                matching_buckets.append(bucket)
        
        return matching_buckets

    @classmethod
    def _fuzzy_name_match(cls, normalized_name: str) -> List[GeoBucket]:
        """
        Layer 3: Find buckets using fuzzy string matching.
        
        Uses Levenshtein distance and trigram similarity.
        
        Args:
            normalized_name: Normalized search term
            
        Returns:
            List of matching buckets
        """
        matching_buckets = []
        
        # Method 1: Levenshtein distance
        all_buckets = GeoBucket.objects.all()
        for bucket in all_buckets:
            distance = Levenshtein.distance(
                normalized_name,
                bucket.normalized_name
            )
            if distance <= cls.MAX_LEVENSHTEIN_DISTANCE:
                matching_buckets.append(bucket)
        
        # Method 2: Trigram similarity via LocationIndex
        indices = LocationIndex.objects.filter(
            normalized_name__icontains=normalized_name[:3]
        )
        
        for index in indices:
            similarity = LocationNormalizer.calculate_similarity(
                normalized_name,
                index.normalized_name
            )
            if similarity >= cls.ACCEPTABLE_MATCH_THRESHOLD:
                matching_buckets.append(index.bucket)
        
        # Method 3: Metaphone matching
        metaphone = LocationNormalizer.metaphone_simple(normalized_name)
        if metaphone:
            metaphone_indices = LocationIndex.objects.filter(
                metaphone=metaphone
            )
            matching_buckets.extend([idx.bucket for idx in metaphone_indices])
        
        return matching_buckets

    @classmethod
    def _extended_spatial_match(
        cls,
        normalized_name: str,
        lat: float,
        lng: float
    ) -> List[GeoBucket]:
        """
        Layer 4: Extended spatial search with relaxed name matching.
        
        Args:
            normalized_name: Normalized search term
            lat: Latitude
            lng: Longitude
            
        Returns:
            List of matching buckets
        """
        # Get extended neighbors (2-ring)
        h3_index = BucketService.calculate_h3_index(lat, lng)
        neighbor_indices = BucketService.get_h3_neighbors_extended(h3_index)
        
        # Find buckets in extended area
        buckets = GeoBucket.objects.filter(
            h3_index__in=neighbor_indices
        )
        
        # Apply relaxed name matching
        matching_buckets = []
        search_words = set(normalized_name.split())
        
        for bucket in buckets:
            bucket_words = set(bucket.normalized_name.split())
            
            # Check if any word matches
            if search_words & bucket_words:
                matching_buckets.append(bucket)
        
        return matching_buckets

    @classmethod
    def _is_name_match(cls, search_name: str, bucket_name: str) -> bool:
        """
        Check if two location names match.
        
        Args:
            search_name: Search term
            bucket_name: Bucket name
            
        Returns:
            True if names match
        """
        # Exact match
        if search_name == bucket_name:
            return True
        
        # Case-insensitive contains
        if search_name in bucket_name or bucket_name in search_name:
            return True
        
        # High similarity
        similarity = LocationNormalizer.calculate_similarity(
            search_name,
            bucket_name
        )
        
        return similarity >= cls.GOOD_MATCH_THRESHOLD

    @classmethod
    def _check_variant_names(
        cls,
        search_name: str,
        variant_names: List[str]
    ) -> bool:
        """
        Check if search name matches any variant names.
        
        Args:
            search_name: Search term
            variant_names: List of variant names
            
        Returns:
            True if any variant matches
        """
        for variant in variant_names:
            normalized_variant = LocationNormalizer.normalize(variant)
            if cls._is_name_match(search_name, normalized_variant):
                return True
        return False

    @classmethod
    def _deduplicate_buckets(cls, buckets: List[GeoBucket]) -> List[GeoBucket]:
        """
        Remove duplicate buckets from list.
        
        Args:
            buckets: List of buckets (may contain duplicates)
            
        Returns:
            Deduplicated list of buckets
        """
        seen_ids = set()
        unique_buckets = []
        
        for bucket in buckets:
            if bucket.id not in seen_ids:
                seen_ids.add(bucket.id)
                unique_buckets.append(bucket)
        
        return unique_buckets

    @classmethod
    def geocode_location(cls, location_name: str) -> Optional[tuple]:
        """
        Attempt to geocode a location name to coordinates.
        
        This is a placeholder - in production, you'd use a geocoding service
        like Google Maps API, Nominatim, or similar.
        
        Args:
            location_name: Location name to geocode
            
        Returns:
            Tuple of (lat, lng) or None
        """
        # For now, search existing buckets for similar names
        normalized = LocationNormalizer.normalize(location_name)
        bucket = GeoBucket.objects.filter(
            normalized_name__iexact=normalized
        ).first()
        
        if bucket:
            return bucket.centroid.y, bucket.centroid.x
        
        return None
