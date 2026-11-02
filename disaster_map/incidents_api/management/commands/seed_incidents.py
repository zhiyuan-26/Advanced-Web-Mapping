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

        # Seed Real Multi-Vertex Hazard Polygons
        hazard_zones = [
            {
                "name": "Shannon River Catchment Flood Risk Zone",
                "coords": [
                    (-8.65, 52.65), (-8.50, 52.80), (-8.15, 53.00), 
                    (-7.90, 53.40), (-7.95, 53.70), (-8.25, 53.80), 
                    (-8.50, 53.40), (-8.80, 52.90), (-8.65, 52.65)
                ]
            },
            {
                "name": "Dublin Metropolitan Storm Risk Zone",
                "coords": [
                    (-6.38, 53.28), (-6.15, 53.28), (-6.12, 53.42), 
                    (-6.32, 53.42), (-6.42, 53.35), (-6.38, 53.28)
                ]
            },
            {
                "name": "Galway Bay Coastal Inundation Zone",
                "coords": [
                    (-9.25, 53.15), (-8.90, 53.18), (-8.85, 53.28), 
                    (-9.10, 53.32), (-9.30, 53.25), (-9.25, 53.15)
                ]
            },
            {
                "name": "Cork Harbour Inundation Area",
                "coords": [
                    (-8.55, 51.80), (-8.30, 51.82), (-8.25, 51.90), 
                    (-8.45, 51.92), (-8.55, 51.80)
                ]
            }
        ]

        for zone in hazard_zones:
            poly = Polygon(zone['coords'])
            MunicipalBoundary.objects.get_or_create(
                name=zone['name'],
                defaults={'mpoly': MultiPolygon(poly, srid=4326)}
            )

        self.stdout.write(self.style.SUCCESS(f"Successfully seeded {len(hazard_zones)} active hazard polygons into PostGIS."))

        categories = ['Flooding', 'Fallen Tree', 'Road Hazard', 'Power Outage']
        severities = ['low', 'medium', 'high', 'critical']

        # Bounding box clusters covering the island of Ireland
        irish_regions = [
            ("Dublin Area", 53.3498, -6.2603),
            ("Cork Region", 51.8985, -8.4756),
            ("Galway West", 53.2707, -9.0568),
            ("Limerick City", 52.6638, -8.6267),
            ("Waterford South", 52.2593, -7.1101),
            ("Sligo North", 54.2766, -8.4761),
            ("Donegal Northwest", 54.6549, -8.1096),
            ("Kerry West", 52.1409, -9.5140),
            ("Belfast Region", 54.5973, -5.9301),
        ]

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