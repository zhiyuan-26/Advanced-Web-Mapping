import random
from django.core.management.base import BaseCommand
from django.contrib.gis.geos import Point, Polygon
from incidents_api.models import Incident, MunicipalBoundary

class Command(BaseCommand):
    help = 'Populates PostGIS database with sample hazards and municipal boundary polygon'

    def add_arguments(self, parser):
        parser.add_argument(
            '--clear',
            action='store_true',
            help='Clear existing incidents and boundaries before loading',
        )

    def handle(self, *args, **options):
        if options['clear']:
            Incident.objects.all().delete()
            MunicipalBoundary.objects.all().delete()
            self.stdout.write(self.style.SUCCESS('Cleared existing data.'))

        base_lat, base_lng = 53.3498, -6.2603 # Dubin area
        categories = ['Flooding', 'Fallen Tree', 'Road Hazard', 'Power Outage']
        severities = ['low', 'medium', 'high', 'critical']

        incidents = []
        for i in range(50):
            lat = base_lat + random.uniform(-0.08, 0.08)
            lng = base_lng + random.uniform(-0.1, 0.1)

            incidents.append(Incident(
                title=f"{random.choice(categories)} at Site #{i+1}",
                category=random.choice(categories),
                description=f"Automated crowd report for hazard site #{i+1}.",
                severity=random.choice(severities),
                status='open',
                upvotes=random.randint(0, 25),
                latitude=lat,
                longitude=lng,
                location=Point(lng, lat, srid=4326),
            ))

        Incident.objects.bulk_create(incidents)

        self.stdout.write(self.style.SUCCESS("Successfully seeded 50 incident records into PostGIS."))