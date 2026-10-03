"""
Weather & Environmental Microclimate Service (app/services/weather.py).
Integrates live weather queries and calculates fungal spore germination risks.
"""

from typing import Dict, Any
from app.agent.tools.weather_tool import get_weather_data


def get_field_weather(location: str = "Bhopal, India") -> Dict[str, Any]:
    """Retrieves real-time environmental context for the target field location."""
    return get_weather_data(location)

