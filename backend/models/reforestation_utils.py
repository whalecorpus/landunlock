#import json
from geopy.geocoders import Nominatim
#from geopy.exc import GeocoderTimedOut
import re
import pycountry
#import time
from unidecode import unidecode

#_winrock_data = None  # Module-level cache for Winrock data
_nominatim = Nominatim(user_agent="landunlock")  # Initialize Nominatim instance




def normalize_to_Winrock_country_name(name, iso_code=None):
    """
    Convert Nominatim country names to Winrock country names using ISO codes.
    Only uses exact matching with ISO codes and the mapping dictionary.
    """
    if not name:
        return None
    
    print(f"Debug - normalize_to_Winrock_country_name input: name='{name}', iso_code='{iso_code}'")
    
    # If we have an ISO code, try to use it first
    if iso_code:
        # Extract the country part from ISO code (e.g., 'RU' from 'RU-MOW')
        country_code = iso_code.split('-')[0]
        print(f"Debug - Extracted country code from ISO: {country_code}")
        
        country = pycountry.countries.get(alpha_2=country_code.upper())
        if country:
            # Convert spaces to underscores for mapping lookup
            pycountry_name = country.name.replace(' ', '_')
            # Try to map to Winrock name
            pycountry_name = COUNTRY_MAPPING_WINROCK.get(pycountry_name, pycountry_name)
            print(f"Debug - Found country in pycountry: {pycountry_name}")
            return pycountry_name
            
    # If no ISO code or no match found, try direct mapping from Nominatim name
    if ' ' in name:
        name = name.replace(' ', '_')
    print(f"Debug - Using Nominatim name after space replacement: {name}")
    return name




# Mapping from pycountry names to Winrock country names, for the subset of countries where they don't match
COUNTRY_MAPPING_WINROCK = {
    # Countries that need mapping from pycountry to Winrock format
    'Bolivia,_Plurinational_State_of': 'Bolivia',
    'Bosnia_and_Herzegovina': 'Bosnia_Herzegovina',
    'Brunei_Darussalam': 'Brunei',
    'Congo': 'Republic_Congo',
    'Congo,_The_Democratic_Republic_of_the': 'Democratic_Republic_Congo',
    'Côte_d\'Ivoire': 'Côte_d_Ivoire',
    'Czechia': 'Czech_Republic',
    'Guinea-Bissau': 'Guinea_Bissau',
    'Iran,_Islamic_Republic_of': 'Iran',
    'Korea,_Democratic_People\'s_Republic_of': 'North_Korea',
    'Korea,_Republic_of': 'South_Korea',
    'Lao_People\'s_Democratic_Republic': 'Laos',
    'Moldova,_Republic_of': 'Moldova',
    'North_Macedonia': 'Macedonia',
    'Palestine,_State_of': 'Palestina',
    'Russian_Federation': 'Russia',
    'Syrian_Arab_Republic': 'Syria',
    'Taiwan,_Province_of_China': 'Taiwan',
    'Tanzania,_United_Republic_of': 'Tanzania',
    'Timor-Leste': 'Timor_Leste',
    'Trinidad_and_Tobago': 'Trinidad_Tobago',
    'Türkiye': 'Turkey',
    'Venezuela,_Bolivarian_Republic_of': 'Venezuela',
    'Viet_Nam': 'Vietnam',
    'Eswatini': 'Swaziland',
    'Falkland_Islands_(Malvinas)': 'Falkland_Islands',
    'Svalbard_and_Jan_Mayen': 'Svalbard_Jan_Mayen'
}


def get_nominatim_subdivisions(address):
    """
    Extract all subdivision names from Nominatim address details.
    
    Args:
        address (dict): Address details from Nominatim
        
    Returns:
        list: List of subdivision names, with Chinese characters converted to Pinyin
    """
    subdivisions = []
    
    # First-level administrative division keys
    subdivision_keys = ['state', 'region', 'province','county', 'municipality']
    
    for key in subdivision_keys:
        if key in address:
            value = address[key]
            # Convert Chinese characters to Pinyin if present
            from pypinyin import pinyin, Style
            pinyin_result = pinyin(value, style=Style.TONE)
            if pinyin_result:
                value = ''.join([item[0] for item in pinyin_result])
            subdivisions.append(value)
            
    return subdivisions

def get_iso_subdivisions(address):
    """
    Get all ISO3166-2 subdivision codes from Nominatim address details.
    
    Args:
        address (dict): Address details from Nominatim
        
    Returns:
        list: List of tuples (level, iso_code) where:
            - level (int): The administrative level (1-8)
            - iso_code (str): The full ISO code (e.g., 'RU-MOW')
    """
    iso_subdivisions = []
    
    # Find all ISO3166-2- keys in the address
    for key in address.keys():
        if key.startswith('ISO3166-2-lvl'):
            try:
                level = int(key.split('lvl')[1])
                iso_code = address[key]
                iso_subdivisions.append((level, iso_code))
            except (ValueError, IndexError):
                continue
    
    # Sort by level, prioritizing level 4 and then falling back to lower levels
    # We want: 4, 3, 2, 1, 5, 6, 7, 8, etc.
    iso_subdivisions.sort(key=lambda x: (x[0] != 4, x[0] != 3, x[0] != 2, x[0] != 1, x[0]))
    
    return iso_subdivisions

# def normalize_subnational_unit(name):
#     """
#     Normalize a subnational unit name for comparison.
#     """
#     if not name:
#         return None
#         
#     # Convert to lowercase and remove special characters
#     name = name.lower()
#     name = re.sub(r'[^\w\s]', '', name)
#     
#     # Normalize whitespace
#     name = re.sub(r'\s+', ' ', name).strip()
#     
#     return name

def match_subnational_unit(subdivision_name, winrock_units):
    """
    Try to match a subdivision name against Winrock units, trying each match type
    in order of quality (exact > exact_normalized > substring).
    
    Args:
        subdivision_name (str): Name of the subdivision to match
        winrock_units (list): List of subnational units from Winrock data
        
    Returns:
        tuple: (matched_unit, match_type) where:
            - matched_unit (str): The original Winrock unit name with exact case, or None
            - match_type (str): 'exact', 'exact_normalized', or 'substring', or None
    """
    # Try exact match first (case-insensitive)
    exact_matches = [unit for unit in winrock_units 
                    if unit.lower() == subdivision_name.lower()]
    if exact_matches:  # For exact matches, take the first one even if multiple
        return exact_matches[0], 'exact'
    
    # Try exact match after normalizing (converting to ASCII)
    normalized_name = unidecode(subdivision_name)
    normalized_matches = [unit for unit in winrock_units 
                         if unidecode(unit).lower() == normalized_name.lower()]
    if len(normalized_matches) == 1:  # For normalized matches, require exactly one match
        return normalized_matches[0], 'exact_normalized'
    elif len(normalized_matches) > 1:
        return None, None  # Multiple normalized matches, skip to next subdivision
    
    # Try substring matching after normalizing, in both directions
    substring_matches = [unit for unit in winrock_units 
                        if normalized_name.lower() in unidecode(unit).lower() or 
                           unidecode(unit).lower() in normalized_name.lower()]
    if len(substring_matches) == 1:  # For substring matches, require exactly one match
        return substring_matches[0], 'substring'
    elif len(substring_matches) > 1:
        return None, None  # Multiple substring matches, skip to next subdivision
    
    return None, None  # No matches found



def get_subnational_unit(address, country_units):
    """
    Get the subnational unit from address details by trying to match
    against Winrock units using both ISO codes and Nominatim subdivisions.
    
    Args:
        address (dict): Address details from Nominatim
        country_units (list): List of Winrock subnational units for the country
        
    Returns:
        tuple: (matched_unit, match_info) where:
            - matched_unit (str): The original Winrock unit name with exact case, or None
            - match_info (dict): Information about the match, including:
                - source: 'iso' or 'nominatim'
                - level: ISO level (for ISO matches) or subdivision type (for Nominatim)
                - match_type: 'exact', 'exact_normalized', or 'substring'
    """
    # Collect all subdivisions into a single list of tuples
    subdivisions = []
    
    # Get ISO subdivisions
    iso_subdivisions = get_iso_subdivisions(address)
    for level, iso_code in iso_subdivisions:
        try:
            subdivision = pycountry.subdivisions.get(code=iso_code)
            if subdivision:
                subdivisions.append((subdivision.name, 'iso', level))
        except Exception as e:
            print(f"Debug - Error processing ISO code {iso_code}: {str(e)}")
            continue
    
    # Get Nominatim subdivisions
    nominatim_subdivisions = get_nominatim_subdivisions(address)
    for subdivision_name in nominatim_subdivisions:
        subdivisions.append((subdivision_name, 'nominatim', 'state/region/province'))
    
    print(f"Debug - Found {len(subdivisions)} total subdivisions to try")
    
    # Try matching each subdivision against the country's units
    for subdivision_name, source, level in subdivisions:
        print(f"Debug - Trying {source} subdivision: {subdivision_name}")
        matched_unit, match_type = match_subnational_unit(subdivision_name, country_units)
        if matched_unit:
            return matched_unit, {
                'source': source,
                'level': level,
                'match_type': match_type
            }
    
    return None, None

