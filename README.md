## Advanced-Web-Mapping Assignment
# Ireland Community Safety & Hazard Reporting System
A Location-Based Services (LBS) web application built with Django (GeoDjango), PostGIS, Leaflet JS, and Bootstrap 5. The system enables crowdsourced reporting and visual analytics for local hazards (e.g., severe flooding, fallen trees, road hazards, power outages) across Ireland.

# Overview & Features
- Interactive LBS Dashboard: Real-time Leaflet map displaying active community hazards with custom severity markers, upvotes, and popups.
- Spatial Risk Zones (Polygons): Multi-vertex PostGIS hazard risk polygons (e.g., Shannon River Catchment, Dublin Storm Zone, Galway Bay Flood Boundary) rendered as dynamic layers.
- Proximity Alert Searches: Point-in-radius spatial query allowing users to click anywhere on the map to find active hazards within a customizable radius ($0.1\text{ to }20\text{ km}$).
- Severity Heatmaps: Leaflet.heat integration to visualize hazard density hotspots across Ireland.
- Crowdsourced Reporting Modal: Responsive Bootstrap 5 form featuring click-to-populate map coordinates, input validation, and real-time map updates.
- Multi-Criteria API Filtering: REST API endpoints supporting category, severity, and spatial bounding queries.
- Fully Containerized: Portable Docker architecture running web services and PostGIS database cleanly.

# Tech Stack & Architecture
- Database Layer: PostgreSQL with PostGIS extension (postgis/postgis image) for spatial indexing and GIST queries (ST_DWithin, ST_Contains).
- Backend Framework: Python / Django (GeoDjango), Django REST Framework (DRF).
- Frontend Interface: HTML5, Bootstrap 5, Vanilla JavaScript, Leaflet.js, Leaflet.heat.
- Containerization: Docker & Docker Compose (web and db services).

# Quick Start & Local Setup (Docker)
# Prerequisites
- Docker Desktop installed and running.
- Git installed.

# 1. Clone the Repository
git clone https://github.com/zhiyuan-26/Advanced-Web-Mapping
cd Advanced-Web-Mapping


# 2. Configure Environment Variables
Copy the template environment file:
cp .env.example .env


# 3. Build and Run Containers
Launch the PostGIS database and Django web container:
docker compose up --build -d


# 4. Run Migrations & Seed PostGIS Database
Apply database schema migrations and populate 100 land-based hazard points and 4 multi-vertex risk polygons across Ireland:
docker compose exec web python manage.py migrate
docker compose exec web python manage.py seed_incidents --clear

# 5. Access the Application
Open your browser and navigate to:
- Dashboard: http://localhost:8000/
- Incidents API: http://localhost:8000/api/incidents/
- Risk Boundaries API: http://localhost:8000/api/incidents/boundaries/

# Spatial Queries Implemented
- Proximity Query (ST_DWithin): Used in /api/incidents/alerts/ to locate all hazard points within $N$ kilometers of a user-clicked map coordinate.
- Point-in-Polygon Containment (ST_Contains): Validates whether reported incident locations or user alert searches fall inside active MunicipalBoundary risk polygons.
- Distance Calculation (Distance): Annotates results with exact physical distance ($\text{km}$) from search locations.

# License
This project is developed for educational and assessment purposes under the Location-Based Services Module.
