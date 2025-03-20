from flask import Flask, request, jsonify
from flask_cors import CORS
from models.solar_calculator import calculate_solar_impact
from models.reforestation_calculator import calculate_reforestation_impact

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

@app.route('/api/calculate', methods=['POST'])
def calculate_impact():
    data = request.json
    area = data.get('area', 0)
    land_use_type = data.get('landUseType', 'reforestation')
    
    if land_use_type == 'reforestation':
        result = calculate_reforestation_impact(area)
    else:  # solar
        result = calculate_solar_impact(area)
    
    return jsonify(result)

if __name__ == '__main__':
    app.run(debug=True)