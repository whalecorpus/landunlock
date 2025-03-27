from enum import Enum
import pvlib
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from timezonefinder import TimezoneFinder
import io
import base64

class Orientation(Enum):
    NORTH = 0
    EAST = 90
    SOUTH = 180
    WEST = 270



def get_solar_weather_data(latitude, longitude, year):
    """
    Fetch historical solar weather data from either NREL PSM3 (North America) or PVGIS (rest of world).
        
    Returns:
        tuple: (solar_weather_timeseries, solar_weather_metadata, is_north_america)
    """
    # Check if location is roughly in North America
    is_north_america = (-170 <= longitude <= -50) and (15 <= latitude <= 72)
    
    try:
        if is_north_america:
            # Use NREL PSM3 for North American locations
            timeseries, metadata = pvlib.iotools.get_psm3(
                latitude=latitude,
                longitude=longitude,
                names=year,
                api_key="q5fLNXiHGb5MkcKQQI19aIfG7qlvXZ0hfITOsuNh", # move these to an environment variable
                email="aarathi.sugathan@gmail.com",
                map_variables=True,
                leap_day=True,
            )
        else:
            # Use PVGIS for rest of world
            weather_data = pvlib.iotools.get_pvgis_tmy(
                latitude=latitude,
                longitude=longitude,
                coerce_year=year
            )
            
            # Unpack the tuple and ensure datetime index
            timeseries, months, inputs, metadata = weather_data
            # Convert directly from UTC to Melbourne time
            # Convert timezone
            tf = TimezoneFinder()
            timezone_str = tf.timezone_at(lat=latitude, lng=longitude)
            if timezone_str:
                timeseries.index = pd.to_datetime(timeseries.index)
                timeseries = timeseries.tz_convert(timezone_str)
            
        return timeseries, metadata, is_north_america
            
    except Exception as e:
        raise Exception(f"Error fetching solar weather data: {str(e)}")

def create_weather_plots(weather_data):
    # Create a figure with two subplots stacked vertically
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 10))

    # First subplot: Daily Solar Radiation Pattern
    weather_data[['ghi', 'dni', 'dhi']].head(24).plot(ax=ax1)
    ax1.set_title('Daily Solar Radiation Pattern')
    ax1.set_xlabel('Hour of Day')
    ax1.set_ylabel('Irradiance (W/m²)')
    ax1.legend(['Global Horizontal', 'Direct Normal', 'Diffuse Horizontal'])

    # Second subplot: Temperature and Wind Speed
    ax3 = ax2.twinx()

    # Plot temperature on primary axis
    weather_data['temp_air'].plot(ax=ax2, color='red')
    ax2.set_xlabel('Time')
    ax2.set_ylabel('Temperature (°C)', color='red')

    # Plot wind speed on secondary axis
    weather_data['wind_speed'].plot(ax=ax3, color='blue')
    ax3.set_ylabel('Wind Speed (m/s)', color='blue')

    # Add a title for the second subplot
    ax2.set_title('Temperature and Wind Speed Over Time')

    # Adjust layout to prevent overlap
    plt.tight_layout()

    # Save plot to a bytes buffer
    buf = io.BytesIO()
    plt.savefig(buf, format='png')
    plt.close()
    buf.seek(0)
    
    # Convert to base64 string
    plot_base64 = base64.b64encode(buf.getvalue()).decode('utf-8')
    return plot_base64

def create_ac_output_plot(pv_output):
    """Create a plot of AC output over time."""
    # Create figure and axis
    fig, ax = plt.subplots(figsize=(12, 6))
    
    # Create figure with two subplots
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 10))

    # Plot single day (Jan 2)
    jan2_data = pv_output[pv_output.index.date == pd.Timestamp('2022-01-02').date()]
    ax1.plot(jan2_data.index.hour, jan2_data['AC Output (Wh)'], 'o-', label='AC Output')
    ax1.set_title('AC Output in one day')
    ax1.set_xlabel('Hour of Day')
    ax1.set_ylabel('AC Output (Wh)')
    ax1.grid(True)
    ax1.legend()
    ax1.set_xticks(range(0, 24, 2))  # Show ticks every 2 hours
    ax1.set_xticklabels([f'{i:02d}:00' for i in range(0, 24, 2)])  # Format as HH:00

    # Plot full time series
    ax2.plot(pv_output.index, pv_output['AC Output (Wh)'].clip(lower=0), label='AC Output')
    ax2.set_title('AC Output in one year')
    ax2.set_xlabel('Date')
    ax2.set_ylabel('AC Output (Wh)')
    ax2.grid(True)
    ax2.legend()
    ax2.xaxis.set_major_locator(mdates.MonthLocator())
    ax2.xaxis.set_major_formatter(mdates.DateFormatter('%b %Y'))
    ax2.tick_params(axis='x', rotation=45)
    
    # Adjust layout to prevent label cutoff
    plt.tight_layout()
    
    # Save plot to bytes buffer
    buf = io.BytesIO()
    plt.savefig(buf, format='png', bbox_inches='tight')
    plt.close()
    
    # Convert to base64 string
    buf.seek(0)
    return base64.b64encode(buf.getvalue()).decode('utf-8')

def simulate_pv_output(
    solar_weather_timeseries,
    latitude,
    longitude,
    altitude_meters,
    array_tilt,
    orientation,
    pv_panel_model,
    inverter_model,
    number_of_panels,
):
    """
    Simulate PV system output using pvlib.
      
    Returns:
        pd.DataFrame: Results including DC and AC output
    """
    # Try to get panel specifications from both databases
    cec_database = pvlib.pvsystem.retrieve_sam('CECMod')
    sandia_database = pvlib.pvsystem.retrieve_sam('SandiaMod')
    
    # Check which database contains our panel model
    if pv_panel_model in cec_database.columns:
        panel_specs = cec_database[pv_panel_model]
    elif pv_panel_model in sandia_database.columns:
        panel_specs = sandia_database[pv_panel_model]
    else:
        raise ValueError(f"Panel model {pv_panel_model} not found in either CEC or Sandia database")
    
    # Try to get inverter specifications from both inverter databases
    cec_inverter_database = pvlib.pvsystem.retrieve_sam('cecinverter')
    anton_inverter_database = pvlib.pvsystem.retrieve_sam('adrinverter')
    
    # Check which database contains our inverter model
    if inverter_model in cec_inverter_database.columns:
        inverter_specs = cec_inverter_database[inverter_model]
    elif inverter_model in anton_inverter_database.columns:
        inverter_specs = anton_inverter_database[inverter_model]
    else:
        raise ValueError(f"Inverter model {inverter_model} not found in either CEC or Anton Driesse inverter database")
    

    
    # Calculate power at STC
    power_stc = panel_specs['Impo'] * panel_specs['Vmpo']


    # Calculate solar position
    solar_position = pvlib.solarposition.get_solarposition(
        time=solar_weather_timeseries.index,
        latitude=latitude,
        longitude=longitude,
        altitude=altitude_meters,
        temperature=solar_weather_timeseries["temp_air"],
    )

    # Calculate total irradiance on panel surface
    total_irradiance = pvlib.irradiance.get_total_irradiance(
        array_tilt,
        orientation,
        solar_position["apparent_zenith"],
        solar_position["azimuth"],
        solar_weather_timeseries["dni"],
        solar_weather_timeseries["ghi"],
        solar_weather_timeseries["dhi"],
        dni_extra=pvlib.irradiance.get_extra_radiation(solar_weather_timeseries.index),
        model="haydavies",
    )

   

    # Calculate air mass and angle of incidence
    airmass = pvlib.atmosphere.get_absolute_airmass(
        pvlib.atmosphere.get_relative_airmass(solar_position["apparent_zenith"]),
        pvlib.atmosphere.alt2pres(altitude_meters),
    )

    aoi = pvlib.irradiance.aoi(
        array_tilt,
        orientation,
        solar_position["apparent_zenith"],
        solar_position["azimuth"],
    )

    # Calculate effective irradiance
    effective_irradiance = pvlib.pvsystem.sapm_effective_irradiance(
        total_irradiance["poa_direct"],
        total_irradiance["poa_diffuse"],
        airmass,
        aoi,
        panel_specs,
    )



    # Calculate cell temperature
    cell_temperature = pvlib.temperature.sapm_cell(
        total_irradiance["poa_global"],
        solar_weather_timeseries["temp_air"],
        solar_weather_timeseries["wind_speed"],
        **pvlib.temperature.TEMPERATURE_MODEL_PARAMETERS["sapm"]["open_rack_glass_glass"],
    )

    
    # Calculate DC output
    dc_output = pvlib.pvsystem.sapm(
        effective_irradiance,
        cell_temperature,
        panel_specs
    )

    # Calculate AC output
    ac_output = pvlib.inverter.sandia(
        dc_output["v_mp"],
        dc_output["p_mp"],
        inverter_specs
    )
 
    # Create results DataFrame
    results = pd.DataFrame({
        "DC Output (Wh)": dc_output["i_mp"] * dc_output["v_mp"] * number_of_panels,
        "AC Output (Wh)": ac_output * number_of_panels,
        "Solar Azimuth (°)": solar_position["azimuth"],
        "Solar Elevation (°)": solar_position["apparent_elevation"],
    })
    results.index = solar_weather_timeseries.index

    return results

def calculate_solar_impact(
    area_hectares,
    location,  # Changed from separate lat/long to Point object
    altitude_meters=10,
    orientation="SOUTH",  
    #pv_system_capacity_watts=5000, # these params were in the homework, but don't make sense when we're considering a large area
    #pv_panel_capacity_watts=220,
    pv_panel_model="Canadian_Solar_CS5P_220M___2009_",
    pv_panel_width = 1, # estimates for residential panels; use 1mx2m for commercial
    pv_panel_height = 1.7,
    inverter_model="ABB__MICRO_0_25_I_OUTD_US_208__208V_",
    array_tilt=None,  # Will be set to abs(latitude) if None
    simulation_year=2022,
    spacing_factor=1.1  # Multiplier for panel area to account for spacing (default 10% spacing)
):
    """
    Calculate the energy production and carbon offset from solar panels.

        
    Returns:
        dict: Results including energy production and carbon offset
    """
    # Convert text orientation to degrees
    try:
        orientation = Orientation[orientation.upper()].value
    except KeyError:
        raise ValueError(f'Invalid orientation. Must be one of: {", ".join(Orientation.__members__.keys())}')

    latitude = location.lat
    longitude = location.long

    # Set tilt to latitude if not specified
    if array_tilt is None:
        array_tilt = abs(latitude)

    # Calculate panel area including spacing
    panel_area_m2 = pv_panel_width * pv_panel_height * spacing_factor
    
    # Convert area to square meters and calculate number of panels
    area_m2 = area_hectares * 10000
    number_of_panels = int(area_m2 / panel_area_m2)
    
    # Calculate number of panels based on system capacity (this was how num_panels was calculated in the homework)
    # capacity_based_panels = pv_system_capacity_watts / pv_panel_capacity_watts


    try:

        # Fetch solar weather data
        solar_weather_timeseries, solar_weather_metadata, is_north_america = get_solar_weather_data(
            latitude, longitude, simulation_year
        )

        
        
        # Calculate PV output
        pv_output = simulate_pv_output(
            solar_weather_timeseries,
            latitude,
            longitude,
            altitude_meters,
            array_tilt,
            orientation,
            pv_panel_model,
            inverter_model,
            number_of_panels,
        )
        
        # Create plots in case we want to add to frontend
        # weather_plot_base64 = create_weather_plots(solar_weather_timeseries)
        # ac_output_plot_base64 = create_ac_output_plot(pv_output)
        
        # Calculate annual energy production (MWh)
        annual_dc_energy = pv_output["DC Output (Wh)"].sum() / 1_000_000  # Convert to MWh
        annual_ac_energy = pv_output["AC Output (Wh)"].sum() / 1_000_000  # Convert to MWh
        
        # Assuming average grid carbon intensity of 0.5 tons CO2e per MWh
        carbon_offset = annual_ac_energy * 0.5
        
        return {
            'landUseType': 'solar',
            'areaHectares': area_hectares,
            'location': {
                'latitude': latitude,
                'longitude': longitude,
                'altitude': altitude_meters,
                'orientation': orientation
            },
            'systemSpecs': {
                'numberOfPanels': number_of_panels,
                'panelModel': pv_panel_model,
                'inverterModel': inverter_model,
                'tilt': array_tilt
            },
            'weatherData': {
                'source': 'NREL PSM3' if is_north_america else 'PVGIS',
                'year': simulation_year
                #'weather_timeseries': solar_weather_timeseries,
                #'plot': weather_plot_base64
            },
            'energyProduction': annual_ac_energy,
                #'energyPlot': ac_output_plot_base64
            'carbonOffset': carbon_offset
        }
    except Exception as e:
        raise Exception(f"Failed to calculate solar impact: {str(e)}")