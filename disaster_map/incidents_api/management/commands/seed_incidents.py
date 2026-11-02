import random
from django.core.management.base import BaseCommand
from django.contrib.gis.geos import Point, Polygon, MultiPolygon
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

        # Create the Ireland bounding box polygon
        ireland_bbox = Polygon([
            (-10.5, 51.4),  # Southwest corner (Kerry/Cork)
            (-5.5, 51.4),   # Southeast corner (Wexford)
            (-5.5, 55.4),   # Northeast corner (Antrim)
            (-10.5, 55.4),  # Northwest corner (Donegal)
            (-10.5, 51.4)   # Closing the ring
        ])

        MunicipalBoundary.objects.get_or_create(
            name="Ireland National Boundary Box",
            defaults={"mpoly": MultiPolygon(ireland_bbox, srid=4326)}
        )

        categories = ['Flooding', 'Fallen Tree', 'Road Hazard', 'Power Outage']
        severities = ['low', 'medium', 'high', 'critical']

        incidents = []
        for i in range(100):
            region_name, base_lat, base_lng = random.choice(irish_regions)
            lat = base_lat + random.uniform(-0.08, 0.08)
            lng = base_lng + random.uniform(-0.1, 0.1)

            category = random.choice(categories)
            severity = random.choice(severities)

            incidents.append(Incident(
                title=f"{category} near {region_name} Site #{i+1}",
                category=category,
                description=f"Crowdsourced safety report in {region_name}.",
                severity=severity,
                status='open',
                upvotes=random.randint(0, 25),
                latitude=lat,
                longitude=lng,
                location=Point(lng, lat, srid=4326),
            ))

        Incident.objects.bulk_create(incidents)

        self.stdout.write(self.style.SUCCESS("Successfully seeded 100 incident records into PostGIS."))