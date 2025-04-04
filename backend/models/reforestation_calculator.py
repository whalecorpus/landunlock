from .util import Point
from .reforestation_utils import get_subnational_unit, normalize_to_Winrock_country_name
import json
from pathlib import Path
from geopy.geocoders import Nominatim
import psutil
#import time

# Initialize Nominatim geocoder
_nominatim = Nominatim(user_agent="landunlock")

# Cache for Winrock data
_winrock_data = None

def get_location_info(latitude, longitude):
    """
    Get location information using Nominatim and Winrock data.
    Returns a tuple of (address dict, list of Winrock subnational units, country name).
    """
    try:
        # Get location information from Nominatim
        result = _nominatim.reverse((latitude, longitude))
        if not result or not result.raw.get('address'):
            return None, None, None
            
        address = result.raw['address']
        
        # Get country name and normalize it
        country = address.get('country')
        if not country:
            return None, None, None
            
        # Get ISO code from address
        iso_code = None
        for key in address.keys():
            if key.startswith('ISO3166'):
                iso_code = address[key]
                break
                
        if not iso_code:
            return None, None, None
            
        normalized_country = normalize_to_Winrock_country_name(country, iso_code)
            
        # Get Winrock data for the country
        winrock_data = get_winrock_data()
        if normalized_country not in winrock_data:
            return None, None, None
            
        # Get all subnational units for the country
        country_units = list(winrock_data[normalized_country].keys())
        
        return address, country_units, normalized_country
        
    except Exception as e:
        print(f"Error in get_location_info: {str(e)}")
        return None, None, None

def get_winrock_data():
    """
    Get the Winrock data from the JSON file.
    The data is structured as:
    {
        'country_name': {
            'subnational_unit': {
                'column_heading': value,
                ...
            },
            ...
        },
        ...
    }
    """
    global _winrock_data
    
    # Return cached data if available
    if _winrock_data is not None:
        return _winrock_data
    
    # Get the path to the data file using relative paths
    data_dir = Path(__file__).parent.parent / 'data'
    input_file = data_dir / 'Winrock_data.json'
    
    # Read the JSON file
    with open(input_file, 'r') as f:
        _winrock_data = json.load(f)
    
    return _winrock_data

def get_country_median_values(winrock_data, country):
    """
    Calculate median values for all forest types across all subregions of a country.
    
    Args:
        winrock_data (dict): The Winrock data dictionary
        country (str): The country name
        
    Returns:
        dict: Dictionary containing median values for each forest type
    """
    # Get all subregions for the country
    subregions = winrock_data.get(country, {})
    
    # Initialize lists to store values for each forest type
    forest_values = {
        'teak': [], 'eucalyptus': [], 'other broadleaf': [], 'oak': [], 
        'pine': [], 'other conifer': [], 'Natural Regeneration': [],
        'Mangrove Restoration - tree': [], 'Mangrove Restoration - shrub': [],
        'Agroforestry': []
    }
    
    # Collect all non-N/A values for each forest type
    for subregion in subregions.values():
        for forest_type in forest_values.keys():
            value = subregion.get(forest_type)
            if value != 'N/A' and isinstance(value, (int, float)):
                forest_values[forest_type].append(value)
    
    # Calculate median for each forest type
    median_values = {}
    for forest_type, values in forest_values.items():
        if values:
            median_values[forest_type] = sum(values) / len(values)
        else:
            median_values[forest_type] = 'N/A'
    
    return median_values

def log_memory_usage(label):
    process = psutil.Process(os.getpid())
    memory_mb = process.memory_info().rss / 1024 / 1024
    print(f"MEMORY [{label}]: {memory_mb:.2f} MB")
    return memory_mb

def calculate_reforestation_impact(area_hectares, location):
    """
    Calculate the carbon sequestration impact of reforestation at a given location.
    
    Args:
        area_hectares (float): Area in hectares
        location (Point): Location object containing lat/long coordinates
        
    Returns:
        dict: Results including carbon sequestered per year for each forest type
    """
    log_memory_usage("START calculate_reforestation_impact")
    latitude = location.lat
    longitude = location.long
    
    # Get location info and Winrock units
    address, country_units, country = get_location_info(latitude, longitude)
    if not address or not country_units:
        return "Winrock location info not found"
    log_memory_usage("After get_location_info")
    
    # Get the Winrock subnational unit for the location
    subnational_unit, match_info = get_subnational_unit(address, country_units)
    
    # Get Winrock data for the location
    winrock_data = get_winrock_data()
    log_memory_usage("After get_winrock_data")
    
    # If no subnational unit was matched, use country median values
    if not subnational_unit or match_info == 'no_match':
        sequestration_data = get_country_median_values(winrock_data, country)
        subnational_unit = "Country Median"
    else:
        sequestration_data = winrock_data[country][subnational_unit]

    log_memory_usage("Before forest types processing")    
    # Forest types to process (excluding averages and flags)
    forest_types = [
        'teak', 'eucalyptus', 'other broadleaf', 'oak', 'pine', 
        'other conifer', 'Natural Regeneration', 
        'Mangrove Restoration - tree', 'Mangrove Restoration - shrub', 
        'Agroforestry'
    ]
    # 
    # Calculate carbon sequestration for each forest type
    forest_results = {}
    for forest_type in forest_types:
        # print(f"\nDebug - Processing forest type: {forest_type}")
        tC_ha_y = sequestration_data[forest_type]
        # print(f"Debug - tC_ha_y: {tC_ha_y}")
        
        # Skip if N/A
        if tC_ha_y == 'N/A':
            # print(f"Debug - Skipping {forest_type} due to N/A value")
            forest_results[forest_type] = {
                'potential_removal_one_year_tCO2e': 'N/A',
                'cumulative_removal_tCO2e': ['N/A'] * 20
                #'average_20year_cumulative_removal_per_year_tCO2e': 'N/A'
            }
            continue
            
        # Calculate potential removal per year
        potential_removal_one_year_tCO2e = area_hectares * tC_ha_y * 44/12 # multiply by the ratio of the molecular weight of carbon dioxide to that of carbon (44/12)
        # print(f"Debug - potential_removal_one_year_tCO2e: {potential_removal_one_year_tCO2e}")
        
        # Calculate cumulative removal over 20 years
        cumulative_removal_tCO2e = []
        for year in range(1, 21):
            # print(f"Debug - Processing year {year}")
            if year == 1:
                # print(f"Debug - Year 1: Adding {potential_removal_one_year_tCO2e}")
                cumulative_removal_tCO2e.append(potential_removal_one_year_tCO2e)
            else:
                # print(f"Debug - Year {year}: Adding {cumulative_removal_tCO2e[year-2]} + {potential_removal_one_year_tCO2e}")
                cumulative_removal_tCO2e.append(cumulative_removal_tCO2e[year-2] + potential_removal_one_year_tCO2e)
        
        # Calculate average yearly removal over 20 years
        #average_20year_cumulative_removal_per_year_tCO2e = sum(cumulative_removal_tCO2e) / 20
        # print(f"Debug - Average yearly removal: {average_20year_cumulative_removal_per_year_tCO2e}")
        
        forest_results[forest_type] = {
            'potential_removal_one_year_tCO2e': potential_removal_one_year_tCO2e,
            'cumulative_removal_tCO2e': cumulative_removal_tCO2e 
            #'average_20year_cumulative_removal_per_year_tCO2e': average_20year_cumulative_removal_per_year_tCO2e
        }
    
    # Restructure the results into categories
    plantation_types = ['teak', 'eucalyptus', 'other broadleaf', 'oak', 'pine', 'other conifer']

    log_memory_usage("Before restructured_results creation")        

    restructured_results = {
        'Plantations and Woodlots': {},
        'Other Forest Types': {}
    }

    for k, v in forest_results.items():
        if k in plantation_types:
            category = 'Plantations and Woodlots'
        else:
            category = 'Other Forest Types'
            
        restructured_results[category][k] = {}
        for key, value in v.items():
            if isinstance(value, list):
                restructured_results[category][k][key] = [round(x, 1) if x != 'N/A' else 'N/A' for x in value]
            else:
                restructured_results[category][k][key] = round(value, 1) if value != 'N/A' else 'N/A'
    
    log_memory_usage("After restructured_results creation")

    gc.collect()
    log_memory_usage("Before returning results")
    
    return {
        'landUseType': 'reforestation',
        'areaHectares': area_hectares,
        'country': country,
        'subnationalUnit': subnational_unit,
        'matchInfo': match_info,
        'tC_perHectare_perYear': sequestration_data,
        'forestResults': restructured_results
    }

def test_one_location():
    """
    Test the reforestation calculator with specific coordinates.
    """
    # California coordinates (approximately Sacramento)
    lat = 38.5816
    lon = -121.4944
    # Kerala, India coordinates:
    lat = 8.5241
    lon = 76.9366
    # Paris coordinates (no Winrock subregion)
    #lat =  48.8566
    #lon = 2.3522
    # Dhaka, Bangladesh (no N/A values for any forest types):
    lat = 23.8103
    lon = 90.4125
    
    # Create a Point object
    from .util import Point
    location = Point(latitude=lat, longitude=lon)
    
    # Test with 1 hectare
    result = calculate_reforestation_impact(1, location)
    
    # Print results in a readable format
    print(f"Location: {lat}, {lon}")
    print(f"Area: 100 hectares")
    print("\nResult:")
    print(f"Country: {result.get('country')}")
    print(f"Subnational Unit: {result.get('subnationalUnit')}")
    print(f"Match Info: {result.get('matchInfo')}")
    print("\ntC per hectare per year:")
    for key, value in result.get('tC_perHectare_perYear', {}).items():
        print(f"{key}: {value}")
    print("\nForest Results:")
    for forest_type, results in result.get('forestResults', {}).items():
        print(f"\n{forest_type}:")
        for key, value in results.items():
            print(f"{key}: {value}")

def test_location_extraction():
    """
    Test location extraction using the same logic as calculate_reforestation_impact.
    """
    test_locations = [
        # United States - California
        #{"name": "California", "lat": 36.7783, "lon": -119.4179, "country": "United States"}
        # India - Rajasthan
        #{"name": "Rajasthan", "lat": 27.0238, "lon": 74.2179, "country": "India"}
        # Australia - Victoria
        #{"name": "Victoria", "lat": -37.8136, "lon": 144.9631, "country": "Australia"},
        # Canada - Ontario
        #{"name": "Ontario", "lat": 43.6532, "lon": -79.3832, "country": "Canada"},
        # United Kingdom - England
        #{"name": "England", "lat": 51.5074, "lon": -0.1278, "country": "United Kingdom"}
        # Nigeria - Lagos State
        #{"name": "Lagos", "lat": 6.5244, "lon": 3.3792, "country": "Nigeria"}
        # Brazil - São Paulo
        #{"name": "São Paulo", "lat": -23.5505, "lon": -46.6333, "country": "Brazil"},
        # China - Guangdong
        {"name": "Guangdong", "lat": 23.1350, "lon": 113.2644, "country": "China"}
        
        # Russia - locations with special characters
        #{"name": "Yevrey", "lat": 48.4808, "lon": 132.1387, "country": "Russia"},
        #{"name": "Zabaykal'ye", "lat": 52.0463, "lon": 113.5508, "country": "Russia"},
        #{"name": "Saint Petersburg", "lat": 59.9311, "lon": 30.3609, "country": "Russia"},
        #{"name": "Moscow Oblast", "lat": 55.7558, "lon": 37.6173, "country": "Russia"}
        
        # Serbia - locations with special characters
        #{"name": "Toplički", "lat": 43.2167, "lon": 21.5833, "country": "Serbia"},
        #{"name": "Zapadno-Bački", "lat": 45.7833, "lon": 19.1167, "country": "Serbia"},
        #{"name": "Vojvodina", "lat": 45.2671, "lon": 19.8335, "country": "Serbia"},
        #{"name": "Belgrade", "lat": 44.7866, "lon": 20.4489, "country": "Serbia"},
        
        # France - locations with special characters
        #{"name": "Île-de-France", "lat": 48.8566, "lon": 2.3522, "country": "France"},
        
        # Germany - locations
        #{"name": "Bavaria", "lat": 48.7904, "lon": 11.4979, "country": "Germany"},
        #{"name": "Baden-Württemberg", "lat": 48.6616, "lon": 9.3501, "country": "Germany"},
        
        # Norway - locations
        #{"name": "Oslo", "lat": 59.9139, "lon": 10.7522, "country": "Norway"},
        #{"name": "Troms og Finnmark", "lat": 69.6492, "lon": 18.9553, "country": "Norway"},
        
        # Italy - locations
        #{"name": "Lombardy", "lat": 45.4669, "lon": 9.1903, "country": "Italy"},
        #{"name": "Sicily", "lat": 37.5999, "lon": 14.0154, "country": "Italy"},
        
        # Bangladesh - Dhaka
        #{"name": "Dhaka", "lat": 23.8103, "lon": 90.4125, "country": "Bangladesh"}
    ]
    
    print("\nTesting location extraction:")
    print("="*50)
    
    for location in test_locations:
        print(f"\nTesting {location['name']} at ({location['lat']}, {location['lon']}):")
        
        try:
            # Get location info using the same logic as calculate_reforestation_impact
            address, country_units, country = get_location_info(location['lat'], location['lon'])
            
            if not address or not country_units:
                print("Location info not found")
                continue
                
            print(f"\nFound country: {country}")
            print(f"Found {len(country_units)} Winrock units")
            
            # Get the Winrock subnational unit for the location
            subnational_unit, match_info = get_subnational_unit(address, country_units)
            
            if subnational_unit:
                print(f"\nFound subnational unit: {subnational_unit}")
                print(f"Match info: source={match_info['source']}, level={match_info['level']}, match_type={match_info['match_type']}")
            else:
                print("\nNo subnational unit found")
                
        except Exception as e:
            print(f"Error: {str(e)}")
        
        print("-"*50)
        time.sleep(1)


