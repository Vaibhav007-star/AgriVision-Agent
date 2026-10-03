"""
Crop Information Tool (app/agent/tools/crop_info_tool.py).
Provides botanical family, optimal growing temperatures, and susceptible pathogens.
"""

from typing import Dict, Any

CROP_DATABASE = {
    "Tomato": {
        "botanical_name": "Solanum lycopersicum",
        "family": "Solanaceae",
        "optimal_temp": "20°C - 28°C",
        "soil_ph": "6.0 - 6.8",
        "common_diseases": ["Early Blight", "Late Blight", "Leaf Mold", "Bacterial Spot"]
    },
    "Potato": {
        "botanical_name": "Solanum tuberosum",
        "family": "Solanaceae",
        "optimal_temp": "15°C - 22°C",
        "soil_ph": "5.0 - 6.0",
        "common_diseases": ["Early Blight", "Late Blight", "Common Scab"]
    },
    "Corn": {
        "botanical_name": "Zea mays",
        "family": "Poaceae",
        "optimal_temp": "22°C - 32°C",
        "soil_ph": "5.8 - 7.0",
        "common_diseases": ["Common Rust", "Northern Leaf Blight", "Gray Leaf Spot"]
    },
    "Apple": {
        "botanical_name": "Malus domestica",
        "family": "Rosaceae",
        "optimal_temp": "18°C - 24°C",
        "soil_ph": "6.0 - 7.0",
        "common_diseases": ["Apple Scab", "Black Rot", "Cedar Apple Rust"]
    },
    "Pepper": {
        "botanical_name": "Capsicum annuum",
        "family": "Solanaceae",
        "optimal_temp": "21°C - 29°C",
        "soil_ph": "6.0 - 6.8",
        "common_diseases": ["Bacterial Spot", "Anthracnose", "Phytophthora Blight"]
    }
}


def get_crop_info(crop_name: str) -> Dict[str, Any]:
    """Retrieves agronomic profile for the specified crop."""
    for key, data in CROP_DATABASE.items():
        if key.lower() in crop_name.lower():
            return {"found": True, "crop": key, **data}
    return {
        "found": False,
        "crop": crop_name,
        "family": "Unknown",
        "optimal_temp": "20°C - 28°C",
        "soil_ph": "6.0 - 7.0",
        "common_diseases": ["Foliar Blights", "Root Rots"]
    }

