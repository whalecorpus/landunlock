// components/MapDisplay.js
import React, { useRef, useEffect, useState } from 'react';
import mapboxgl from 'mapbox-gl';
import MapboxDraw from '@mapbox/mapbox-gl-draw';
import 'mapbox-gl/dist/mapbox-gl.css';

// Prevent Mapbox GL JS from failing in browsers without WebGL support
if (typeof window !== 'undefined') {
  // Verify WebGL support before proceeding
  const supported = mapboxgl.supported();
  if (!supported) {
    console.error('WebGL not supported in this browser');
  }
}

const MapDisplay = ({ onAreaSelected }) => {
  const mapContainer = useRef(null);
  const map = useRef(null);
  const draw = useRef(null);
  const [mapLoaded, setMapLoaded] = useState(false);
  
  // Get your token from an environment variable or define it here
  // For development, you can hardcode it temporarily
  const MAPBOX_TOKEN = '';
  
  useEffect(() => {
    if (!mapContainer.current || map.current) return;
    
    // Set token at runtime to prevent SSR issues
    mapboxgl.accessToken = MAPBOX_TOKEN;
    
    try {
      map.current = new mapboxgl.Map({
        container: mapContainer.current,
        style: 'mapbox://styles/mapbox/satellite-v9',
        center: [ -73.48675198097595, 41.37624849656973], // Danbury Fair Mall, CT USA (adjust as needed)
        zoom: 15,
      });
      
      map.current.on('error', (e) => {
        console.error('Mapbox error:', e);
      });
    } catch (e) {
      console.error('Error initializing map:', e);
    }
    
    return () => {
      if (map.current) {
        map.current.remove();
        map.current = null;
      }
    };
  }, [onAreaSelected]);
  
  return (
    <div>
      <div 
        ref={mapContainer} 
        style={{ 
          height: '400px', 
          width: '50%', 
          borderRadius: '4px',
          position: 'relative'
        }} 
      />
    </div>
  );
};

export default MapDisplay;