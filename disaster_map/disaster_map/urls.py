"""
URL configuration for hello_map project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from mapping.views import map_view
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView
from django.views.generic import TemplateView
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('spatial/', include('spatial_analysis.urls')),

    # API endpoints
    path('api/cities/', include('cities_api.urls')), # Week 3 REST API

    # API documentation
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),

    path('map/', TemplateView.as_view(template_name='map.html'), name='map'),  # NEW
    path('', TemplateView.as_view(template_name='map.html'), name='map_home'),  # Root redirect
]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
