from django.contrib.gis.db import models

class Incident(models.Model): 
    SEVERITY_CHOICES = [
        ("low", "Low"),
        ("medium", "Medium"),
        ("high", "High"),
        ("critical", "Critical"),
    ]

    title = models.CharField(max_length=120)
    category = models.CharField(max_length=50)
    description = models.TextField(blank=True, null=True)
    severity = models.CharField(max_length=10, choices=SEVERITY_CHOICES, default="medium")
    status = models.CharField(max_length=10, default="open")
    upvotes = models.PositiveIntegerField(default=0)
    image = models.ImageField(upload_to="incidents/", blank=True, null=True)

    # PostGIS Spatial Geometries
    location = models.PointField(srid=4326)
    latitude = models.FloatField(null=True, blank=True)
    longitude = models.FloatField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        indexes = [models.Index(fields=["status", "severity"])]

    def __str__(self):
        return f"{self.title} ({self.category})"

class MunicipalBoundary(models.Model):
    name = models.CharField(max_length=100)
    mpoly = models.MultiPolygonField(srid=4326)

    def __str__(self):
        return self.name

