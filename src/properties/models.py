from django.db import models

# Create your models here.
from django.contrib.gis.db import models
from django.contrib.postgres.fields import ArrayField
from django.core.validators import MinValueValidator
from decimal import Decimal


class GeoBucket(models.Model):
    """
    Represents a geographic bucket for grouping nearby properties.
    Uses H3 hexagonal grid system for consistent spatial indexing.
    """
    h3_index = models.CharField(
        max_length=15,
        unique=True,
        db_index=True,
        help_text="H3 hexagonal index at resolution 9 (~174m diameter)"
    )
    centroid = models.PointField(
        geography=True,
        srid=4326,
        help_text="Geographic center point of the bucket"
    )
    normalized_name = models.CharField(
        max_length=255,
        db_index=True,
        help_text="Normalized location name for matching"
    )
    variant_names = ArrayField(
        models.CharField(max_length=255),
        default=list,
        blank=True,
        help_text="Array of location name variations"
    )
    property_count = models.IntegerField(
        default=0,
        validators=[MinValueValidator(0)],
        help_text="Number of properties in this bucket"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'geo_buckets'
        indexes = [
            models.Index(fields=['normalized_name']),
            models.Index(fields=['h3_index']),
        ]
        ordering = ['-property_count', 'normalized_name']

    def __str__(self):
        return f"{self.normalized_name} (H3: {self.h3_index[:8]}...)"

    def add_variant_name(self, name: str):
        """Add a new location name variant if not already present."""
        if name and name not in self.variant_names:
            self.variant_names.append(name)
            self.save(update_fields=['variant_names', 'updated_at'])

    def increment_property_count(self):
        """Atomically increment the property count."""
        self.property_count = models.F('property_count') + 1
        self.save(update_fields=['property_count', 'updated_at'])
        self.refresh_from_db()

    def decrement_property_count(self):
        """Atomically decrement the property count."""
        if self.property_count > 0:
            self.property_count = models.F('property_count') - 1
            self.save(update_fields=['property_count', 'updated_at'])
            self.refresh_from_db()


class Property(models.Model):
    """
    Represents a real estate property with geographic location.
    Automatically assigned to a geo-bucket based on coordinates.
    """
    title = models.CharField(
        max_length=255,
        help_text="Property title/description"
    )
    location_name = models.CharField(
        max_length=255,
        db_index=True,
        help_text="Original location name as provided by user"
    )
    location = models.PointField(
        geography=True,
        srid=4326,
        help_text="Geographic coordinates (lat, lng)"
    )
    bucket = models.ForeignKey(
        GeoBucket,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='properties',
        help_text="Assigned geo-bucket"
    )
    price = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.01'))],
        help_text="Property price in local currency"
    )
    bedrooms = models.IntegerField(
        validators=[MinValueValidator(0)],
        help_text="Number of bedrooms"
    )
    bathrooms = models.IntegerField(
        validators=[MinValueValidator(0)],
        help_text="Number of bathrooms"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'properties'
        indexes = [
            models.Index(fields=['bucket', '-created_at']),
            models.Index(fields=['-created_at']),
            models.Index(fields=['location_name']),
        ]
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.title} - {self.location_name}"

    @property
    def latitude(self):
        """Get latitude from point."""
        return self.location.y if self.location else None

    @property
    def longitude(self):
        """Get longitude from point."""
        return self.location.x if self.location else None

    def save(self, *args, **kwargs):
        """Override save to ensure bucket assignment."""
        is_new = self.pk is None
        old_bucket_id = None
        
        if not is_new:
            old_property = Property.objects.filter(pk=self.pk).first()
            old_bucket_id = old_property.bucket_id if old_property else None
        
        super().save(*args, **kwargs)
        
        # Update bucket counts
        if is_new and self.bucket:
            self.bucket.increment_property_count()
        elif not is_new and old_bucket_id != self.bucket_id:
            if old_bucket_id:
                old_bucket = GeoBucket.objects.get(pk=old_bucket_id)
                old_bucket.decrement_property_count()
            if self.bucket:
                self.bucket.increment_property_count()

    def delete(self, *args, **kwargs):
        """Override delete to update bucket count."""
        if self.bucket:
            self.bucket.decrement_property_count()
        super().delete(*args, **kwargs)


class LocationIndex(models.Model):
    """
    Index for fuzzy location name matching.
    Stores normalized names, phonetic encodings, and trigrams.
    """
    original_name = models.CharField(
        max_length=255,
        help_text="Original location name"
    )
    normalized_name = models.CharField(
        max_length=255,
        db_index=True,
        help_text="Normalized version of the name"
    )
    bucket = models.ForeignKey(
        GeoBucket,
        on_delete=models.CASCADE,
        related_name='location_indices'
    )
    metaphone = models.CharField(
        max_length=50,
        db_index=True,
        null=True,
        blank=True,
        help_text="Metaphone phonetic encoding"
    )
    trigrams = ArrayField(
        models.CharField(max_length=3),
        default=list,
        blank=True,
        help_text="Trigrams for fuzzy matching"
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'location_index'
        indexes = [
            models.Index(fields=['normalized_name']),
            models.Index(fields=['metaphone']),
        ]
        unique_together = ['original_name', 'bucket']

    def __str__(self):
        return f"{self.original_name} -> {self.normalized_name}"
