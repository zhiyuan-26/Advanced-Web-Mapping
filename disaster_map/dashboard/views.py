# dashboard/views.py
from django.db.models import Avg, Count, Max, Min, Sum
from django.shortcuts import render

from incidents_api.models import Incident


def index(request):
    """Main dashboard view"""
    context = {
        'total_incidents': Incident.objects.count(),
        'open_incidents': Incident.objects.filter(status='open').count(),
        'critical_hazards': Incident.objects.filter(severity='critical', status='open').count(),
        'categories': Incident.objects.values_list('category', flat=True).distinct().order_by('category'),
        'severities': [choice[0] for choice in Incident.SEVERITY_CHOICES],
    }
    return render(request, 'dashboard/index.html', context)


def analytics(request):
    """Analytics page with detailed statistics"""

    # Aggregate incident statistics across all community reports
    incident_agg = Incident.objects.aggregate(
        total_count=Count('id'),
        total_upvotes=Sum('upvotes'),        
        avg_upvotes=Avg('upvotes'),        
        max_upvotes=Max('upvotes'),        
        min_upvotes=Min('upvotes'),        
    )
    
    incident_stats = {
        'total_incidents': incident_agg['total_count'] or 0, 
        'total_upvotes': incident_agg['total_upvotes'] or 0,
        'avg_upvotes': round(incident_agg['avg_upvotes'] or 0.0, 1),
        'max_upvotes': incident_agg['max_upvotes'] or 0,
        'min_upvotes': incident_agg['min_upvotes'] or 0,
        'open_count': Incident.objects.filter(status='open').count(),
        'resolved_count': Incident.objects.filter(status='resolved').count(),
    }

    # Breakdown counts by severity level
    severity_stats = {
        'low': Incident.objects.filter(severity='low').count(),
        'medium': Incident.objects.filter(severity='medium').count(),
        'high': Incident.objects.filter(severity='high').count(),
        'critical': Incident.objects.filter(severity='critical').count(),
    }

    # Breakdown counts by hazard category
    category_breakdown = list(
        Incident.objects.values('category')
        .annotate(
            count=Count('id'),
            total_upvotes=Sum('upvotes'),
            avg_upvotes=Avg('upvotes')
        )
        .order_by('-count')
    )

    context = {
        'incident_stats': incident_stats,
        'severity_stats': severity_stats,
        'category_breakdown': category_breakdown,
    }
    return render(request, 'dashboard/analytics.html', context)