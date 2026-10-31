from rest_framework import serializers
from rest_framework_gis.serializers import GeoFeatureModelSerializer
from django.contrib.gis.geos import Point
from .models import Incident, MunicipalBoundary

class IncidentListSerializer(serializers.ModelSerializer):
    """Serializer for incident list and detail endpoints."""

    latitude = serializers.ReadOnlyField()
    longitude = serializers.ReadOnlyField()
    distance_km = serializers.SerializerMethodField()
    population_category = serializers.ReadOnlyField()

    class Meta:
        model = Incident
        fields = [
            'id', 'title', 'category', 'description',
            'severity', 'status', 'upvotes', 'image', 
            'latitude', 'longitude', 'distance_km', 'created_at'
        ]

    def get_distance_km(self, obj):
        if hasattr(obj, 'distance') and obj.distance:
            return round(obj.distance_km, 2)
        return 0.0

class IncidentCreateSerializer(serializers.ModelSerializer):
    """"Serializer for creating an incident from lat/lng fields."""
    latitude = serializers.FloatField(write_only=True)
    longitude = serializers.FloatField(write_only=True)

    class Meta:
        model = Incident
        fields = [
            'id', 'title', 'category', 'description',
            'severity', 'status', 'image', 
            'latitude', 'longitude'
        ]

    def validate_latitude(self, value):
        """Validate latitude range"""
        if not -90 <= value <= 90:
            raise serializers.ValidationError("Latitude must be between -90 and 90")
        return value

    def validate_longitude(self, value):
        """Validate longitude range"""
        if not -180 <= value <= 180:
            raise serializers.ValidationError("Longitude must be between -180 and 180")
        return value

    def create(self, validated_data):
        """Create incident with Point geometry from lat/lng"""

        lat = validated_data.pop('latitude')
        lng = validated_data.pop('longitude')
        validated_data['location'] = Point(lng, lat, srid=4326)
        return super().create(validated_data)

class DistanceSerializer(serializers.Serializer):
    """Reusable serializer for spatial proximity/radius queries"""

    lat = serializers.FloatField()
    lng = serializers.FloatField()
    radius_km = serializers.FloatField(min_value=0.1, max_value=20000)

    def validate_lat(self, value):
        if not -90 <= value <= 90:
            raise serializers.ValidationError("Latitude must be between -90 and 90")
        return value

    def validate_lng(self, value):
        if not -180 <= value <= 180:
            raise serializers.ValidationError("Longitude must be between -180 and 180")
        return value