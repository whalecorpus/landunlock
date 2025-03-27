from flask import Flask, request, jsonify
from flask_cors import CORS
from models.util import Point
from models.util import Point
from models.solar_calculator import calculate_solar_impact
from models.reforestation_calculator import calculate_reforestation_impact
import sys

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

@app.route('/api/calculate', methods=['POST'])
def calculate_impact():
    data = request.json
    latitude = data.get('latitude', 0)
    longitude = data.get('longitude', 0)
    location = Point(latitude, longitude)
    orientation = data.get('orientation', 'SOUTH')
    area = data.get('area', 0)
    land_use_type = data.get('landUseType', 'reforestation')
    
    if land_use_type == 'reforestation':
        result = calculate_reforestation_impact(area, location)
    elif land_use_type == 'solar':  

        # Extract all solar parameters with defaults
        result = calculate_solar_impact(
            area_hectares=area / 10000,  # Convert sq meters to hectares
            location=location,
            altitude_meters=data.get('altitude', 10),
            orientation=orientation,  
            pv_panel_model=data.get('pv_panel_model', "Canadian_Solar_CS5P_220M___2009_"),
            inverter_model=data.get('inverter_model', "ABB__MICRO_0_25_I_OUTD_US_208__208V_"),
            array_tilt=data.get('array_tilt'), # if not provided, defaults to abs(latitude)
            simulation_year=data.get('simulation_year', 2022)
        )
    else:
    	result = {
    		'error': f'Land use type {land_use_type} not handled'
    	}    
    
    return jsonify(result)

if __name__ == '__main__':
    app.run(debug=True)
