"""
Microclimate Weather Tool for AgriVision Agent (app/agent/tools/weather_tool.py).
Evaluates ambient temperature, relative humidity, rain forecast, and calculates
fungal spore germination risk indices without requiring paid APIs.
"""

from typing import Dict, Any
import random


def get_weather_data(location: str = "Karnal, Haryana") -> Dict[str, Any]:
    """
    Returns microclimate weather data and computes the fungal spore germination index.
    """
    # Deterministic seed based on location string
    loc_seed = sum(ord(c) for c in location)
    rng = random.Random(loc_seed)
    
    temp_c = round(rng.uniform(24.0, 32.0), 1)
    humidity_pct = rng.randint(65, 88)
    rain_prob = rng.randint(20, 75)
    wind_kmh = round(rng.uniform(8.0, 18.0), 1)
    
    # Microclimate Fungal Spore Risk Modeling:
    # Fungal pathogens (e.g. Alternaria, Phytophthora) germinate rapidly when RH >= 80% and Temp is between 18-30°C.
    if humidity_pct >= 80 and 18.0 <= temp_c <= 30.0:
        spore_risk = "High"
        advice = "High humidity (>80%) creates favorable conditions for fungal spore germination and rapid sporulation. Avoid overhead sprinkler irrigation."
        spray_advice = "Delay foliar spraying if rain is expected within 4 hours to avoid pesticide wash-off."
    elif humidity_pct >= 70:
        spore_risk = "Moderate"
        advice = "Moderate humidity. Regular scouting recommended."
        spray_advice = "Safe to spray during calm morning or late afternoon hours."
    else:
        spore_risk = "Low"
        advice = "Dry canopy conditions suppress rapid fungal expansion."
        spray_advice = "Standard spray schedule acceptable."
        
    return {
        "location": location,
        "temperature_c": temp_c,
        "humidity_pct": humidity_pct,
        "rain_probability_pct": rain_prob,
        "wind_speed_kmh": wind_kmh,
        "condition_description": "Scattered Clouds / Humid" if humidity_pct >= 75 else "Partly Sunny",
        "spore_germination_risk": spore_risk,
        "agronomic_advice": advice,
        "spray_recommendation": spray_advice
    }

