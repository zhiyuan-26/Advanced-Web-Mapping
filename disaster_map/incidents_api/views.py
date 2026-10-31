from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import generics, status
from django.contrib.gis.geos import Point
from django.contrib.gis.measure import D
from django.contrib.gis.db.models.functions import Distance
from django.db.models import Q


from rest_framework.pagination import PageNumberPagination
from rest_framework.filters import SearchFilter, OrderingFilter
from django_filters.rest_framework import DjangoFilterBackend
import json


from .models import Incident
from .serializers import IncidentListSerializer, DistanceSerializer


from .models import City
from .serializers import (
    CityListSerializer, CityDetailSerializer, CityGeoJSONSerializer,
    CityCreateSerializer, CitySummarySerializer, DistanceSerializer,
    BoundingBoxSerializer
)
from .filters import CityFilter

class StandardResultsSetPagination(PageNumberPagination):
    """Custom pagination class"""
    page_size = 20
    page_size_query_param = 'page_size'
    max_page_size = 100

class CityListCreateView(generics.ListCreateAPIView):
    """
    List all cities or create a new city
    """
    queryset = City.objects.all()
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_class = CityFilter
    search_fields = ['name', 'country', 'region']
    ordering_fields = ['name', 'country', 'population', 'founded_year']
    ordering = ['-population']  # Default ordering

    def get_serializer_class(self):
        """Use different serializers for list vs create"""
        if self.request.method == 'POST':
            return CityCreateSerializer
        return CityListSerializer

    def get_queryset(self):
        """Optionally filter queryset based on query parameters"""
        queryset = City.objects.all()

        # Additional custom filters
        min_population = self.request.query_params.get('min_population')
        if min_population:
            try:
                min_pop = int(min_population)
                queryset = queryset.filter(population__gte=min_pop)
            except ValueError:
                pass

        capitals_only = self.request.query_params.get('capitals_only')
        if capitals_only and capitals_only.lower() == 'true':
            queryset = queryset.filter(is_capital=True)

        return queryset



@api_view(['GET'])
def list_incidents(request):
    """
    Return list of incidents
    """
    incidents = Incident.objects.filter(status='open')
    serializer = IncidentListSerializer(incidents, many=True)
    return Response(serializer.data)

@api_view(['POST'])
def nearest_incidents(request):
    """
    Return nearest incidents
    """
    serializer = DistanceSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    data = serializer.validated_data
    user_point = Point(data['lng'], data['lat'], srid=4326)

    incidents = Incident.objects.filter(status='open').annotate(
        distance=Distance("location", user_point)
    ).order_by("distance")[:10]

    return Response({
        'search_point': {'lat': data['lat'], 'lng': data['lng']},
        'total_found': incidents.count(),
        'nearest_incidents': IncidentListSerializer(incidents, many=True).data
    })

@api_view(['POST'])
def check_hazard_alerts(request):
    serializer = DistanceSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    data = serializer.validated_data
    user_point = Point(data['lng'], data['lat'], srid=4326)

    # Spatial query: within 1km radius OR inside active Hazard Polygon
    alerts = Incident.objects.filter(
        status='open'
    ).filter(
        Q(location__distance_lte=(user_point, D(km=data['radius_km']))) |
        Q(impact_zone__contains=user_point)
    ).annotate(
        distace=Distance('location', user_point)
    ).order_by('distance')

    return Response({
        'user_location': {'lat': data['lat'], 'lng': data['lng']},
        'radius_km': data['radius_km'],
        'total_alerts': alerts.count(),
        'incidents': IncidentListSerializer(alerts, many=True).data
    })

@api_view(['POST'])
def upvote_incident(request, incident_id):
    try:
        inc = Incident.objects.get(id=incident_id)
        inc.upvotes += 1
        inc.save()
        return Response({'id': inc.id, 'upvotes': inc.upvotes})
    except Incident.DoesNotExist:
        return Response({"error": "Incident not found."}, status=status.HTTP_404_NOT_FOUND)