"""
Field Spray & Knapsack Tank Dosage Tool (app/agent/tools/dosage_tool.py).
Calculates exact water volumes, chemical mass, and 15L knapsack tank counts based on farmer acreage.
"""

from typing import Dict, Any


def calculate_spray_dosage(
    crop: str,
    disease: str,
    field_acres: float = 1.0,
    severity: str = "Moderate"
) -> Dict[str, Any]:
    """
    Computes precise chemical and organic spray tank mixture parameters.
    Standard calibration: 200 Liters of water per acre for foliar canopies.
    """
    water_volume_liters = round(field_acres * 200.0, 1)
    tanks_15L = round(water_volume_liters / 15.0, 1)
    
    if "healthy" in disease.lower():
        return {
            "field_acres": field_acres,
            "water_volume_liters": water_volume_liters,
            "sprayer_tanks_15L": tanks_15L,
            "chemical_required": "None required (Crop is healthy)",
            "organic_required": f"Cold-pressed Neem Oil: {round(water_volume_liters * 3.0, 0):.0f} ml (3 ml/L)",
            "safety_equipment": ["Standard gloves", "Sun hat"]
        }
        
    # Standard fungicide rate: 2.5 grams per Liter
    chem_grams = round(water_volume_liters * 2.5, 1)
    chem_kg = chem_grams / 1000.0
    chem_str = f"{chem_kg:.2f} kg ({chem_grams:.0f} g) of Mancozeb 75% WP" if chem_kg >= 1.0 else f"{chem_grams:.0f} g of Mancozeb 75% WP"
    
    # Organic rate: 5.0 ml per Liter
    neem_ml = round(water_volume_liters * 5.0, 0)
    neem_liters = neem_ml / 1000.0
    organic_str = f"{neem_liters:.2f} L ({neem_ml:.0f} ml) of Neem Oil 10,000 ppm"
    
    return {
        "field_acres": field_acres,
        "water_volume_liters": water_volume_liters,
        "sprayer_tanks_15L": tanks_15L,
        "chemical_required": chem_str,
        "organic_required": organic_str,
        "safety_equipment": ["Chemical splash goggles", "N95 respirator mask", "Nitrile gloves", "Rubber boots"]
    }

