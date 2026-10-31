from django.urls import path
from . import views

app_name = 'incidents_api'

urlpatterns = [
    # Basic CRUD endpoints
    path('', views.list_incidents, name='list_incidents'),
    path('nearest/', views.nearest_incidents, name='nearest_incidents'),
    path('alerts/', views.check_hazard_alerts, name='check_hazard_alerts'),
    path('<int:incident_id>/upvote/', views.upvote_incident, name='upvote_incident'),
]