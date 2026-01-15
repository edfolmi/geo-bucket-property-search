from django.contrib.gis import admin
from properties.models import GeoBucket, Property, LocationIndex


# Register your models here.
@admin.register(GeoBucket)
class GeoBucketAdmin(admin.GISModelAdmin):
    """Admin interface for GeoBucket model."""
    
    list_display = [
        'id',
        'normalized_name',
        'h3_index_short',
        'property_count',
        'created_at'
    ]
    list_filter = ['created_at', 'property_count']
    search_fields = ['normalized_name', 'h3_index', 'variant_names']
    readonly_fields = ['h3_index', 'property_count', 'created_at', 'updated_at']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('normalized_name', 'variant_names')
        }),
        ('Geographic Data', {
            'fields': ('h3_index', 'centroid')
        }),
        ('Statistics', {
            'fields': ('property_count',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at')
        }),
    )
    
    def h3_index_short(self, obj):
        """Display shortened H3 index."""
        return f"{obj.h3_index[:8]}..."
    h3_index_short.short_description = 'H3 Index'
    
    # Enable map display
    default_lon = 3.3792
    default_lat = 6.5244
    default_zoom = 10


@admin.register(Property)
class PropertyAdmin(admin.GISModelAdmin):
    """Admin interface for Property model."""
    
    list_display = [
        'id',
        'title',
        'location_name',
        'bucket_name',
        'price',
        'bedrooms',
        'bathrooms',
        'created_at'
    ]
    list_filter = ['bedrooms', 'bathrooms', 'created_at', 'bucket']
    search_fields = ['title', 'location_name', 'bucket__normalized_name']
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        ('Property Details', {
            'fields': ('title', 'price', 'bedrooms', 'bathrooms')
        }),
        ('Location', {
            'fields': ('location_name', 'location', 'bucket')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at')
        }),
    )
    
    def bucket_name(self, obj):
        """Display bucket normalized name."""
        return obj.bucket.normalized_name if obj.bucket else 'No Bucket'
    bucket_name.short_description = 'Bucket'
    
    # Enable map display
    default_lon = 3.3792
    default_lat = 6.5244
    default_zoom = 10


@admin.register(LocationIndex)
class LocationIndexAdmin(admin.ModelAdmin):
    """Admin interface for LocationIndex model."""
    
    list_display = [
        'id',
        'original_name',
        'normalized_name',
        'metaphone',
        'bucket_name',
        'created_at'
    ]
    list_filter = ['created_at']
    search_fields = ['original_name', 'normalized_name', 'metaphone']
    readonly_fields = ['created_at']
    
    fieldsets = (
        ('Names', {
            'fields': ('original_name', 'normalized_name')
        }),
        ('Fuzzy Matching', {
            'fields': ('metaphone', 'trigrams')
        }),
        ('Association', {
            'fields': ('bucket',)
        }),
        ('Timestamp', {
            'fields': ('created_at',)
        }),
    )
    
    def bucket_name(self, obj):
        """Display associated bucket name."""
        return obj.bucket.normalized_name
    bucket_name.short_description = 'Bucket'
