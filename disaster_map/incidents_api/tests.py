from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from django.contrib.gis.geos import Point
from incidents_api.models import Incident

class IncidentSpatialAPITests(APITestCase):
    def setUp(self):
        self.hazard_dublin = Incident.objects.create(
            title="Flooded Road",
            category="Flooding",
            severity="critical",
            status="open",
            locaiton=Point(-6.2603, 53.3498, srid=4326)
        )

        self.alert_url = reverse('check_hazard_alerts')

    def test_valid_proximity_alert(self):
        payload = {"lat": 53.3498, "lng": -6.2603, "radius_km": 1.0}
        response = self.client.post(self.alert_url, payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreaterEqual(response.data['total_alerts'], 1)

    def test_invalid_coordinates(self):
        payload = {"lat": 195.0, "lng": -6.2603}
        response = self.client.post(self.alert_url, payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)