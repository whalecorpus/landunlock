import React, { useRef, useEffect, useState } from 'react';
import mapboxgl from 'mapbox-gl';
import MapboxDraw from '@mapbox/mapbox-gl-draw';
import 'mapbox-gl/dist/mapbox-gl.css';

// You'll need to get a Mapbox API key
const MAPBOX_TOKEN = 'YOUR_MAPBOX_ACCESS_TOKEN';
mapboxgl.accessToken = MAPBOX_TOKEN;

const MapDisplay = ({ onAreaSelected }) => {
  const mapContainer = useRef(null);
  const map = useRef(null);
  const draw = useRef(null);
  
  useEffect(() => {
    if (map.current) return;
    
    map.current = new mapboxgl.Map({
      container: mapContainer.current,
      style: 'mapbox://styles/mapbox/satellite-v9',
      center: [-74.5, 40], // Default location (adjust as needed)
      zoom: 9
    });
    
    map.current.on('load', () => {
      // Add drawing tools
      draw.current = new MapboxDraw({
        displayControlsDefault: false,
        controls: {
          polygon: true,
          trash: true
        }
      });
      
      map.current.addControl(draw.current);
      
      // Calculate area when a polygon is drawn or updated
      map.current.on('draw.create', updateArea);
      map.current.on('draw.update', updateArea);
      map.current.on('draw.delete', () => onAreaSelected(null));
    });
    
    function updateArea() {
      const data = draw.current.getAll();
      if (data.features.length > 0) {
        const area = calculateArea(data.features[0].geometry);
        onAreaSelected(area);
      }
    }
    
    function calculateArea(polygon) {
      // Very simplified area calculation - in a real app you'd use turf.js
      // This is just a placeholder
      const coords = polygon.coordinates[0];
      // Simple approximation for small areas - not accurate for large areas
      let area = 0;
      for (let i = 0; i < coords.length - 1; i++) {
        area += coords[i][0] * coords[i+1][1] - coords[i+1][0] * coords[i][1];
      }
      area = Math.abs(area) / 2;
      
      // Convert to hectares (very approximate)
      // In a real app, use proper geospatial calculations
      return area * 100;
    }
    
    return () => {
      if (map.current) {
        map.current.remove();
      }
    };
  }, [onAreaSelected]);
  
  return (
    <div>
      <div ref={mapContainer} style={{ height: '400px', width: '100%', borderRadius: '4px' }} />
    </div>
  );
};

export default MapDisplay;

