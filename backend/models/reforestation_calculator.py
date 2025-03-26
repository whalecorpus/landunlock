def calculate_reforestation_impact(area_hectares, location):
    """
    Calculate the carbon sequestration potential for reforestation.
    
    Args:
        area_hectares (float): Area in hectares
        
    Returns:
        dict: Results including carbon sequestered per year
    """
    # Basic calculation based on average sequestration rates
    # More sophisticated models would consider location, species, climate, etc.
    
    # Rough estimate: 3.5 tons CO2e per hectare per year for dense forest
    carbon_sequestered = area_hectares * 3.5
    
    return {
        'landUseType': 'reforestation',
        'areaHectares': area_hectares,
        'carbonSequestered': carbon_sequestered
    }