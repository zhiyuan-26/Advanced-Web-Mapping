console.log('map.js loaded');

let incidentsData = [];
let markers = {};
let map = null;

let searchMarker = null;
let radiusCircle = null;
let proximityLayer;
let heatLayer = null;

const DUBLIN_COORDS = [53.3498, -6.2603];
const DEFAULT_ZOOM = 6;

// API endpoint
const API_URL = '/api/incidents/';

// Initialize the map
async function initMap() {
    // Initialize Leaflet map centered on Dublin
    map = L.map('map').setView(DUBLIN_COORDS, DEFAULT_ZOOM);

    // Add OpenStreetMap tile layer
    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        attribution: '© OpenStreetMap contributors',
        maxZoom: 19,
        minZoom: 2
    }).addTo(map);

    proximityLayer = L.layerGroup().addTo(map);

    try {
        // Fetch cities from API
        console.log('Fetching from:', API_URL);
        const response = await fetch(API_URL);
        console.log('Response status:', response.status);
        console.log('Response headers:', response.headers);

        if (!response.ok) {
            const errorText = await response.text();
            console.error('Error response body:', errorText);
            throw new Error(`HTTP error! status: ${response.status}`);
        }

        const incidentsData = await response.json();
        console.log('Data received:', incidentsData);

        document.getElementById('cityCount').textContent = incidentsData.length;
        renderIncidentMarkers(incidentsData);
        renderHeatMap(incidentsData);

    } catch (error) {
        console.error('Failed to load incidents:', error);
        alert('Failed to load incidents data. Check console for details.');
    } 

    setupEventListeners();
}

function renderIncidentMarkers(incidents) {
    Object.values(markers).forEach(m => map.removeLayer(m));
    markers = {};

    incidents.forEach(inc => {
        const colorMap = { low: '#28a745', medium: '#ffc107', high: '#fd7e14', critical: '#dc3545' };

        // Create marker
        const marker = L.circleMarker([inc.latitude, inc.longitude], {
            radius: 7,
            fillColor: colorMap[inc.severity] || '#007bff',
            color: '#000',
            weight: 1,
            fillOpacity: 0.9
        }).addTo(map);

        marker.bindPopup(`
            <div style="min-width: 100px;">
                <h4 style="margin: 0 0 5px 0;">${inc.title}</h4>
                <p style="margin:2px 0;"><strong>Category:</strong>${inc.category}</p>
                <p style="margin:2px 0;"><strong>Severity:</strong><span style="text-transform: capitalize;">${inc.severity}</span></p>
                <p style="margin:2px 0;"><strong>Upvotes:</strong><span id="upvote-count-${inc.id}">${inc.upvotes}</span></p>
                <button onclick="upvoteIncident(${inc.id})" style="margin-top: 5px; padding: 4px 8px; cursor: pointer;">👍 Upvote</button>
            </div>
        `);

        markers[inc.id] = marker;
    });
}


function renderHeatMap(incidents) {
    if (heatLayer) map.removeLayer(heatLayer);

    const heatData = incidents.map(inc => [inc.latitude, inc.longitude, 1]);
    heatLayer = L.heatLayer(heatData, { raduis: 25, blur: 15, maxZoom: 10}).addTo(map);
}

async function runSpatialAlertCheck(lat, lng) {
    const radiusKm = 1.0;
    clearProximityResults();

    try {
        const res = await fetch('/api/incidents/alerts/', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ lat, lng, radius_km: radiusKm })
        });
        const data = await res.json();

        searchMarker = L.marker([lat, lng]).addTo(map).bindPopup("Your Location").openPopup();
        radiusCircle = L.circle([lat, lng], { radius: radiusKm * 1000, color: 'dc3545', fillOpacity: 0.1 }).addTo(map);

        const results = document.getElementById('proximity-results');
        results.innerHTML = `<strong>${data.total_alerts} Active Hazard Alerts nearby:</strong>`;

        const list = document.createElement('ol');
        data.incidents.forEach(inc => {
            const item = document.createElement('li');
            item.textContent = `${inc.title} (${inc.severity}) - ${inc.distance_km} km away`;
            item.onclick = () => map.setView([inc.coordinates.lat, inc.coordinates.lng], 12);
            list.append(item);
        });
        results.append(list);
    } catch (err) {
        console.error('Alert query error:', err);
    }
}

async function upvoteIncident(incidentId) {
    try {
        const res = await fetch(`/api/incidents/${incidentId}/upvote/`, { method: 'POST' });
        const data = await res.json();
        const el = documet.getElementById(`upvote-count-${incidentId}`);
        if (el) el.textContent = data.upvotes;
    } catch (err) {
        console.error('Upvote failed', err);
    }
}

function clearProximityResults() {
    if (searchMarker) map.removeLayer(searchMarker);
    if (radiusCircle) map.removeLayer(radiusCircle);
    searchMarker = radiusCircle = null;
    document.getElementById('proximity-results').innerHTML = '';
}

function setupEventListener() {
    document.getElementById('resetBtn').addEventListener('click', () => {
        map.setView(DUBLIN_COORDS, DEFAULT_ZOOM, { animate: false });
        clearProximityResults();
    });

    map.on('click' (e) => {
        runSpatialAlertCheck(e.latlng.lat, e.latlng.lng);
    });
}

document.addEventListener('DOMContentLoaded', initMap);