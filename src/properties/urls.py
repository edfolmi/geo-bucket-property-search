from django.urls import path, include
from rest_framework.routers import DefaultRouter
from properties.views import PropertyViewSet, GeoBucketViewSet


router = DefaultRouter()
router.register(r'properties', PropertyViewSet, basename='property')
router.register(r'geo-buckets', GeoBucketViewSet, basename='geo-bucket')

urlpatterns = [
    path('', include(router.urls)),
]
