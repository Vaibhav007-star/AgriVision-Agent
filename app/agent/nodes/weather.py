"""
Weather Analysis Node (app/agent/nodes/weather.py).
Evaluates ambient microclimate parameters and assesses fungal spore germination risks.
"""

from typing import Dict, Any
from app.agent.state import AgentState
from app.agent.tools.weather_tool import get_weather_data


def weather_node(state: AgentState) -> Dict[str, Any]:
    """Executes the microclimate weather tool and updates environmental risk in state."""
    steps = state.get("reasoning_steps", []).copy()
    location = state.get("location", "Bhopal, India")
    
    weather_data = get_weather_data(location)
    spore_risk = weather_data.get("spore_germination_risk", "Moderate")
    humidity = weather_data.get("humidity_pct", 75)
    
    steps.append(f"🌦️ [Weather Node] Queried microclimate for '{location}': RH={humidity}%, Spore Inoculum Risk='{spore_risk}'.")
    
    return {
        "weather": weather_data,
        "reasoning_steps": steps
    }

