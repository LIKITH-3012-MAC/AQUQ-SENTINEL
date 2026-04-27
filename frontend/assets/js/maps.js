document.addEventListener('DOMContentLoaded', () => {
  const map = L.map('map').setView([0, 0], 3);

  const baseLayer = L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
    attribution: '© OpenStreetMap contributors'
  }).addTo(map);

  // NASA GIBS Layers
  const gibsLayers = {
    chlorophyll: L.tileLayer('https://gibs.earthdata.nasa.gov/wmts/epsg3857/best/MODIS_Aqua_Chlorophyll_A/default/{time}/GoogleMapsCompatible_Level9/{z}/{y}/{x}.png', {
      time: new Date().toISOString().split('T')[0],
      attribution: 'NASA GIBS',
      opacity: 0.7
    }),
    trueColor: L.tileLayer('https://gibs.earthdata.nasa.gov/wmts/epsg3857/best/MODIS_Terra_CorrectedReflectance_TrueColor/default/{time}/GoogleMapsCompatible_Level9/{z}/{y}/{x}.png', {
      time: new Date().toISOString().split('T')[0],
      attribution: 'NASA GIBS',
      opacity: 1.0
    }),
    sst: L.tileLayer('https://gibs.earthdata.nasa.gov/wmts/epsg3857/best/MODIS_Terra_Sea_Surface_Temp_Day/default/{time}/GoogleMapsCompatible_Level7/{z}/{y}/{x}.png', {
      time: new Date().toISOString().split('T')[0],
      attribution: 'NASA GIBS',
      opacity: 0.7
    })
  };

  // Default Layer
  gibsLayers.chlorophyll.addTo(map);

  // Layer Controls
  document.getElementById('layerChlorophyll').addEventListener('change', (e) => {
    if (e.target.checked) gibsLayers.chlorophyll.addTo(map);
    else map.removeLayer(gibsLayers.chlorophyll);
  });

  document.getElementById('layerTrueColor').addEventListener('change', (e) => {
    if (e.target.checked) gibsLayers.trueColor.addTo(map);
    else map.removeLayer(gibsLayers.trueColor);
  });

  document.getElementById('layerSST').addEventListener('change', (e) => {
    if (e.target.checked) gibsLayers.sst.addTo(map);
    else map.removeLayer(gibsLayers.sst);
  });

  // Mock Sensitive Zones
  const zones = [
    { name: 'Great Barrier Reef', lat: -18.28, lon: 147.69, risk: 'HIGH' },
    { name: 'Galapagos Marine Reserve', lat: -0.82, lon: -90.96, risk: 'MEDIUM' },
    { name: 'North Pacific Garbage Patch', lat: 35.0, lon: -140.0, risk: 'CRITICAL' }
  ];

  zones.forEach(zone => {
    const color = zone.risk === 'CRITICAL' ? 'var(--risk-critical)' : 
                  zone.risk === 'HIGH' ? 'var(--risk-high)' : 
                  zone.risk === 'MEDIUM' ? 'var(--risk-medium)' : 'var(--risk-low)';
    
    L.circle([zone.lat, zone.lon], {
      color: color,
      fillColor: color,
      fillOpacity: 0.2,
      radius: 500000 // 500km radius for visualization
    }).addTo(map).bindPopup(`<strong>${zone.name}</strong><br>Risk: ${zone.risk}`);
  });
});
