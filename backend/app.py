from flask import Flask, request, jsonify, make_response
from flask_cors import CORS
from models.util import Point
from models.solar_calculator import calculate_solar_impact
from models.reforestation_calculator import calculate_reforestation_impact
import os
import requests

app = Flask(__name__)
CORS(app)

@app.route('/api/calculate', methods=['POST', 'OPTIONS'])
def calculate_impact():
    # Handle preflight request
    if request.method == 'OPTIONS':
        response = make_response()
        response.headers.add('Access-Control-Allow-Origin', os.environ.get('CORS_ORIGIN'))
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type')
        response.headers.add('Access-Control-Allow-Methods', 'POST')
        return response

    # Handle actual request
    data = request.json

    latitude = data.get('latitude', 0)
    longitude = data.get('longitude', 0)
    address = data.get('address', None)

    if (not latitude and not longitude and address):
        print("getting lat/lon for address")

        address = address.replace(" ", "+")
        geocode_api_key = os.environ.get('GEOCODE_MAPS_API_KEY')
        payload = { 'q': address, 'api_key': geocode_api_key  }
        url = 'https://geocode.maps.co/search'
        r = requests.get(url, params=payload)
        r.raise_for_status()

        latitude = float(r.json()[0]['lat'])
        longitude = float(r.json()[0]['lon'])

    location = Point(latitude, longitude)
    orientation = data.get('orientation', 'SOUTH')
    if(latitude < 0):
        orientation = 'NORTH'
    
    areaSquareMeters = data.get('area', 0)
    areaHectares = areaSquareMeters / 10000

    land_use_type = data.get('landUseType', 'solar')
    
    if land_use_type == 'reforestation':
        result = calculate_reforestation_impact(
            areaHectares, 
            location
        )
        print(result)
    elif land_use_type == 'solar':  
        # Extract all solar parameters with defaults
        result = calculate_solar_impact(
            area_hectares=areaHectares,
            location=location,
            altitude_meters=data.get('altitude', 10),
            orientation=orientation,  
            pv_panel_model=data.get('pv_panel_model', "Canadian_Solar_CS5P_220M___2009_"),
            inverter_model=data.get('inverter_model', "ABB__MICRO_0_25_I_OUTD_US_208__208V_"),
            array_tilt=data.get('array_tilt'), # if not provided, defaults to abs(latitude)
            simulation_year=data.get('simulation_year', 2022)
        )
        print(result)
    else:
        result = {
            'error': f'Land use type {land_use_type} not handled'
        }    
    
    return jsonify(result)

@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({"status": "healthy"}), 200

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 3000))
    app.run(host='0.0.0.0', port=port, debug=os.environ.get('FLASK_ENV') == 'development')
