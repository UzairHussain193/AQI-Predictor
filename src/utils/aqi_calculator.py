"""
US EPA AQI Calculator

Converts pollutant concentrations to US EPA Air Quality Index (0-500 scale)
"""


def calculate_pm25_aqi(pm25):
    """
    Calculate AQI from PM2.5 concentration (μg/m³)
    
    Args:
        pm25: PM2.5 concentration in μg/m³
        
    Returns:
        float: AQI value (0-500)
    """
    if pm25 is None or pm25 < 0:
        return None
    
    # EPA PM2.5 breakpoints (μg/m³) and corresponding AQI values
    breakpoints = [
        # (C_low, C_high, I_low, I_high)
        (0.0, 12.0, 0, 50),
        (12.1, 35.4, 51, 100),
        (35.5, 55.4, 101, 150),
        (55.5, 150.4, 151, 200),
        (150.5, 250.4, 201, 300),
        (250.5, 350.4, 301, 400),
        (350.5, 500.4, 401, 500),
    ]
    
    for c_low, c_high, i_low, i_high in breakpoints:
        if c_low <= pm25 <= c_high:
            # Linear interpolation formula
            aqi = ((i_high - i_low) / (c_high - c_low)) * (pm25 - c_low) + i_low
            return round(aqi, 1)
    
    # If concentration is above highest breakpoint
    if pm25 > 500.4:
        return 500.0
    
    return None


def calculate_pm10_aqi(pm10):
    """
    Calculate AQI from PM10 concentration (μg/m³)
    
    Args:
        pm10: PM10 concentration in μg/m³
        
    Returns:
        float: AQI value (0-500)
    """
    if pm10 is None or pm10 < 0:
        return None
    
    # EPA PM10 breakpoints (μg/m³) and corresponding AQI values
    breakpoints = [
        (0, 54, 0, 50),
        (55, 154, 51, 100),
        (155, 254, 101, 150),
        (255, 354, 151, 200),
        (355, 424, 201, 300),
        (425, 504, 301, 400),
        (505, 604, 401, 500),
    ]
    
    for c_low, c_high, i_low, i_high in breakpoints:
        if c_low <= pm10 <= c_high:
            aqi = ((i_high - i_low) / (c_high - c_low)) * (pm10 - c_low) + i_low
            return round(aqi, 1)
    
    if pm10 > 604:
        return 500.0
    
    return None


def calculate_o3_aqi(o3_ppb):
    """
    Calculate AQI from O3 concentration (ppb or μg/m³ converted to ppb)
    
    Args:
        o3_ppb: O3 concentration in ppb (or μg/m³ / 2 for conversion)
        
    Returns:
        float: AQI value (0-500)
    """
    if o3_ppb is None or o3_ppb < 0:
        return None
    
    # EPA O3 8-hour breakpoints (ppb)
    breakpoints = [
        (0, 54, 0, 50),
        (55, 70, 51, 100),
        (71, 85, 101, 150),
        (86, 105, 151, 200),
        (106, 200, 201, 300),
    ]
    
    for c_low, c_high, i_low, i_high in breakpoints:
        if c_low <= o3_ppb <= c_high:
            aqi = ((i_high - i_low) / (c_high - c_low)) * (o3_ppb - c_low) + i_low
            return round(aqi, 1)
    
    if o3_ppb > 200:
        return 300.0
    
    return None


def calculate_no2_aqi(no2_ppb):
    """
    Calculate AQI from NO2 concentration (ppb)
    
    Args:
        no2_ppb: NO2 concentration in ppb
        
    Returns:
        float: AQI value (0-500)
    """
    if no2_ppb is None or no2_ppb < 0:
        return None
    
    # EPA NO2 breakpoints (ppb)
    breakpoints = [
        (0, 53, 0, 50),
        (54, 100, 51, 100),
        (101, 360, 101, 150),
        (361, 649, 151, 200),
        (650, 1249, 201, 300),
        (1250, 1649, 301, 400),
        (1650, 2049, 401, 500),
    ]
    
    for c_low, c_high, i_low, i_high in breakpoints:
        if c_low <= no2_ppb <= c_high:
            aqi = ((i_high - i_low) / (c_high - c_low)) * (no2_ppb - c_low) + i_low
            return round(aqi, 1)
    
    if no2_ppb > 2049:
        return 500.0
    
    return None


def calculate_so2_aqi(so2_ppb):
    """
    Calculate AQI from SO2 concentration (ppb)
    
    Args:
        so2_ppb: SO2 concentration in ppb
        
    Returns:
        float: AQI value (0-500)
    """
    if so2_ppb is None or so2_ppb < 0:
        return None
    
    # EPA SO2 breakpoints (ppb)
    breakpoints = [
        (0, 35, 0, 50),
        (36, 75, 51, 100),
        (76, 185, 101, 150),
        (186, 304, 151, 200),
        (305, 604, 201, 300),
        (605, 804, 301, 400),
        (805, 1004, 401, 500),
    ]
    
    for c_low, c_high, i_low, i_high in breakpoints:
        if c_low <= so2_ppb <= c_high:
            aqi = ((i_high - i_low) / (c_high - c_low)) * (so2_ppb - c_low) + i_low
            return round(aqi, 1)
    
    if so2_ppb > 1004:
        return 500.0
    
    return None


def calculate_co_aqi(co_ppm):
    """
    Calculate AQI from CO concentration (ppm)
    
    Args:
        co_ppm: CO concentration in ppm
        
    Returns:
        float: AQI value (0-500)
    """
    if co_ppm is None or co_ppm < 0:
        return None
    
    # EPA CO breakpoints (ppm)
    breakpoints = [
        (0.0, 4.4, 0, 50),
        (4.5, 9.4, 51, 100),
        (9.5, 12.4, 101, 150),
        (12.5, 15.4, 151, 200),
        (15.5, 30.4, 201, 300),
        (30.5, 40.4, 301, 400),
        (40.5, 50.4, 401, 500),
    ]
    
    for c_low, c_high, i_low, i_high in breakpoints:
        if c_low <= co_ppm <= c_high:
            aqi = ((i_high - i_low) / (c_high - c_low)) * (co_ppm - c_low) + i_low
            return round(aqi, 1)
    
    if co_ppm > 50.4:
        return 500.0
    
    return None


def convert_ug_to_ppb(ug_m3, molecular_weight, temp_k=298.15, pressure_kpa=101.325):
    """
    Convert μg/m³ to ppb
    
    Args:
        ug_m3: Concentration in μg/m³
        molecular_weight: Molecular weight (g/mol)
        temp_k: Temperature in Kelvin (default: 25°C)
        pressure_kpa: Pressure in kPa (default: 1 atm)
        
    Returns:
        float: Concentration in ppb
    """
    if ug_m3 is None:
        return None
    
    # ppb = (μg/m³) * (24.45 / MW) at 25°C and 1 atm
    # Using ideal gas law: V = nRT/P
    molar_volume = (8.314 * temp_k) / (pressure_kpa)  # L/mol
    ppb = (ug_m3 / molecular_weight) * (molar_volume * 1000) / 1000
    return ppb


def calculate_epa_aqi(pm25=None, pm10=None, o3=None, no2=None, so2=None, co=None):
    """
    Calculate US EPA AQI from pollutant concentrations.
    Returns the maximum (worst) AQI among all pollutants.
    
    Args:
        pm25: PM2.5 in μg/m³
        pm10: PM10 in μg/m³
        o3: Ozone in μg/m³
        no2: NO2 in μg/m³
        so2: SO2 in μg/m³
        co: CO in μg/m³
        
    Returns:
        float: EPA AQI value (0-500)
    """
    aqi_values = []
    
    # Calculate AQI for each pollutant
    if pm25 is not None and pm25 > 0:
        pm25_aqi = calculate_pm25_aqi(pm25)
        if pm25_aqi:
            aqi_values.append(pm25_aqi)
    
    if pm10 is not None and pm10 > 0:
        pm10_aqi = calculate_pm10_aqi(pm10)
        if pm10_aqi:
            aqi_values.append(pm10_aqi)
    
    if o3 is not None and o3 > 0:
        # Convert μg/m³ to ppb (O3 MW = 48)
        o3_ppb = convert_ug_to_ppb(o3, 48)
        o3_aqi = calculate_o3_aqi(o3_ppb)
        if o3_aqi:
            aqi_values.append(o3_aqi)
    
    if no2 is not None and no2 > 0:
        # Convert μg/m³ to ppb (NO2 MW = 46)
        no2_ppb = convert_ug_to_ppb(no2, 46)
        no2_aqi = calculate_no2_aqi(no2_ppb)
        if no2_aqi:
            aqi_values.append(no2_aqi)
    
    if so2 is not None and so2 > 0:
        # Convert μg/m³ to ppb (SO2 MW = 64)
        so2_ppb = convert_ug_to_ppb(so2, 64)
        so2_aqi = calculate_so2_aqi(so2_ppb)
        if so2_aqi:
            aqi_values.append(so2_aqi)
    
    if co is not None and co > 0:
        # Convert μg/m³ to ppm (CO MW = 28)
        co_ppm = (co / 28) * 24.45 / 1000  # μg/m³ to ppm
        co_aqi = calculate_co_aqi(co_ppm)
        if co_aqi:
            aqi_values.append(co_aqi)
    
    # Return maximum AQI (worst pollutant determines overall AQI)
    if aqi_values:
        return round(max(aqi_values), 1)
    
    # Fallback: if no pollutants available, return 0
    return 0.0


def get_aqi_category(aqi):
    """
    Get AQI category and description
    
    Args:
        aqi: AQI value
        
    Returns:
        tuple: (category, description, color)
    """
    if aqi <= 50:
        return "Good", "Air quality is satisfactory", "#00e400"
    elif aqi <= 100:
        return "Moderate", "Air quality is acceptable", "#ffff00"
    elif aqi <= 150:
        return "Unhealthy for Sensitive Groups", "Sensitive groups may experience health effects", "#ff7e00"
    elif aqi <= 200:
        return "Unhealthy", "Everyone may begin to experience health effects", "#ff0000"
    elif aqi <= 300:
        return "Very Unhealthy", "Health alert: everyone may experience serious effects", "#8f3f97"
    else:
        return "Hazardous", "Health warning of emergency conditions", "#7e0023"
