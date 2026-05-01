/**
 * AquaSentinel AI - Map Controller (Standalone)
 * NOTE: map.html has its own inline map implementation.
 * This file is for standalone map initialization if needed.
 */

document.addEventListener('DOMContentLoaded', () => {
  const mapEl = document.getElementById('map');
  if (!mapEl || typeof L === 'undefined') return;
  
  // Check if map is already initialized (by inline script)
  if (mapEl._leaflet_id) return;

  const map = L.map('map').setView([0, 0], 3);

  L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
    attribution: '© OpenStreetMap contributors'
  }).addTo(map);

  // NASA GIBS Layers
  const today = new Date().toISOString().split('T')[0];
  const gibsLayers = {
    chlorophyll: L.tileLayer('https://gibs.earthdata.nasa.gov/wmts/epsg3857/best/MODIS_Aqua_Chlorophyll_A/default/{time}/GoogleMapsCompatible_Level9/{z}/{y}/{x}.png', {
      time: today, attribution: 'NASA GIBS', opacity: 0.7
    }),
    trueColor: L.tileLayer('https://gibs.earthdata.nasa.gov/wmts/epsg3857/best/MODIS_Terra_CorrectedReflectance_TrueColor/default/{time}/GoogleMapsCompatible_Level9/{z}/{y}/{x}.png', {
      time: today, attribution: 'NASA GIBS', opacity: 1.0
    }),
    sst: L.tileLayer('https://gibs.earthdata.nasa.gov/wmts/epsg3857/best/MODIS_Terra_Sea_Surface_Temp_Day/default/{time}/GoogleMapsCompatible_Level7/{z}/{y}/{x}.png', {
      time: today, attribution: 'NASA GIBS', opacity: 0.7
    })
  };

  // Bind layer controls if IDs exist
  const bindLayerToggle = (id, layer) => {
    const el = document.getElementById(id);
    if (el) {
      el.addEventListener('change', (e) => {
        if (e.target.checked) layer.addTo(map);
        else map.removeLayer(layer);
      });
      if (el.checked) layer.addTo(map);
    }
  };

  bindLayerToggle('layerChlorophyll', gibsLayers.chlorophyll);
  bindLayerToggle('layerTrueColor', gibsLayers.trueColor);
  bindLayerToggle('layerSST', gibsLayers.sst);

  // Mock Sensitive Zones
  const zones = [
    { name: 'Great Barrier Reef', lat: -18.28, lon: 147.69, risk: 'HIGH' },
    { name: 'Galapagos Marine Reserve', lat: -0.82, lon: -90.96, risk: 'MEDIUM' },
    { name: 'North Pacific Garbage Patch', lat: 35.0, lon: -140.0, risk: 'CRITICAL' }
  ];

  zones.forEach(zone => {
    const color = zone.risk === 'CRITICAL' ? '#ef4444' : 
                  zone.risk === 'HIGH' ? '#f59e0b' : '#10b981';
    
    L.circle([zone.lat, zone.lon], {
      color, fillColor: color, fillOpacity: 0.2, radius: 500000
    }).addTo(map).bindPopup(`<strong>${zone.name}</strong><br>Risk: ${zone.risk}`);
  });
});
