// frontend/src/components/MapDisplay.js
import React, { useRef, useEffect, useState } from 'react';
import mapboxgl from 'mapbox-gl';
import 'mapbox-gl/dist/mapbox-gl.css';

// You'll need to get a Mapbox API key
mapboxgl.accessToken = 'YOUR_MAPBOX_ACCESS_TOKEN';

const MapDisplay = ({ onAreaSelected }) => {
  const mapContainer = useRef(null);
  const map = useRef(null);
  const [selectedArea, setSelectedArea] = useState(null);
  
  useEffect(() => {
    if (map.current) return;
    
    map.current = new mapboxgl.Map({
      container: mapContainer.current,
      style: 'mapbox://styles/mapbox/satellite-v9',
      center: [-74.5, 40], // Default location (adjust as needed)
      zoom: 9
    });
    
    // Add drawing tools to allow selecting an area
    // This is simplified - you'll need to integrate a library like MapboxDraw
    
    map.current.on('load', () => {
      // Setup drawing tools and area calculation here
    });
    
  }, []);
  
  return (
    <div className="map-container">
      <div ref={mapContainer} style={{ height: '400px', width: '100%' }} />
      {selectedArea && (
        <div className="selected-area-info">
          Selected area: {selectedArea.toFixed(2)} hectares
        </div>
      )}
    </div>
  );
};

export default MapDisplay;