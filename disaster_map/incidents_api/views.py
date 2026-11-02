import json
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

from .models import Incident, MunicipalBoundary
from .serializers import IncidentListSerializer, IncidentCreateSerializer, DistanceSerializer

@api_view(['GET', 'POST'])
def list_incidents(request):
    """
    Return list of incidents
    """
    if request.method == 'GET':
        incidents = Incident.objects.filter(status='open')
        category = request.GET.get('category')
        severity = request.GET.get('severity')

        if category:
            incidents = incidents.filter(category__iexact=category)
        if severity:
            incidents = incidents.filter(severity__iexact=severity)

        serializer = IncidentListSerializer(incidents, many=True)
        return Response(serializer.data)

    elif request.method == 'POST':
        serializer = IncidentCreateSerializer(data=request.data)
        if serializer.is_valid():
            incident = serializer.save()
            return Response(IncidentListSerializer(incident).data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
def list_boundaries(request):
    """
    Return hazard risk zones as GeoJSON objects
    """
    boundaries = MunicipalBoundary.objects.all()
    features = []

    for bound in boundaries:
        if bound.mpoly:
            geojson_geom = json.loads(bound.mpoly.geojson)
            features.append({
                "type": "Feature",
                "geometry": geojson_geom,
                "properties": {
                    "id": bound.id,
                    "name": bound.name
                }
            })

    return Response({"type": "FeatureCollection", "features": features})

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

    incidents = Incident.objects.filter(
        status='open', 
        location__isnull=False
    ).annotate(
        distance=Distance("location", user_point)
    ).order_by("distance")[:10]

    return Response({
        'search_point': {'lat': data['lat'], 'lng': data['lng']},
        'total_found': len(incidents),
        'nearest_incidents': IncidentListSerializer(incidents, many=True).data
    })

@api_view(['POST'])
def check_hazard_alerts(request):
    """
    Return incidents within radius of user's point
    """
    serializer = DistanceSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    data = serializer.validated_data
    user_point = Point(data['lng'], data['lat'], srid=4326)

    # Spatial query: within 10 km radius OR inside active Hazard Polygon
    alerts = Incident.objects.filter(
        status='open',
        location__isnull=False,
        location__distance_lte=(user_point, D(km=data['radius_km']))
    ).annotate(
        distance=Distance('location', user_point)
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