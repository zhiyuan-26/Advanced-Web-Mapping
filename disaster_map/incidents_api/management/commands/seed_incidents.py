import random
from django.core.management.base import BaseCommand
from django.contrib.gis.geos import Point, Polygon
from incidents_api.models import Incident

class Command(BaseCommand):
    help = 'Populates database with sample hazards and polygon'

    def add_arguments(self, parser):
        parser.add_argument(
            '--clear',
            action='store_true',
            help='Clear existing cities before loading',
        )

    def handle(self, *args, **options):
        Incident.objects.all().delete()
        base_lat, base_lng = 53.3498, -6.2603 # Dubin area
        categories = ['Flooding', 'Fallen Tree', 'Road Hazard', 'Power Outage']
        severities = ['low', 'medium', 'high', 'critical']

        for i in range(50):
            lat = base_lat + random.uniform(-0.08, 0.08)
            lng = base_lng + random.uniform(-0.1, 0.1)

            # Assign an impact polygon to every 5th incident
            impact = None
            if i % 5 == 0:
                impact = Polygon(((lng, lat), (lng+0.01, lat), (lng+0.01, lat+0.01), (lng, lat+0.01), (lng, lat)))

            Incident.objects.create(
                title=f"{random.choice(categories)} at Site #{i+1}",
                category=random.choice(categories),
                severity=random.choice(severities),
                status='open',
                upvotes=random.randint(0, 25),
                location=Point(lng, lat, srid=4326),
                impact_zone=impact
            )

        self.stdout.write(self.style.SUCCESS("Successfully seeded 50 incident records into PostGIS."))