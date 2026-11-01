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