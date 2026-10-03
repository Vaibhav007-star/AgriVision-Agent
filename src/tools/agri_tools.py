"""
Agronomic Dosage & Tank Mixture Calculation Tool for AgriVision Agent.
Calculates water volume, fungicide mass, and bio-spray dilution for field acreage.
"""

from typing import Dict, Any


def calculate_field_dosage(crop: str, disease: str, area_acres: float = 1.0) -> Dict[str, Any]:
    """
    Calculates precise pesticide/fungicide quantities and water volume based on field size.
    """
    # Standard spray volume: 200 Liters of water per acre for vegetable crops
    water_volume_liters = round(area_acres * 200.0, 1)
    
    if "healthy" in disease.lower():
        return {
            "crop": crop,
            "condition": "Healthy",
            "field_area_acres": area_acres,
            "water_volume_liters": water_volume_liters,
            "chemical_required": "None (Crop is healthy)",
            "organic_required": f"Neem Oil: {round(water_volume_liters * 3 / 1000, 2)} Liters (at 3 ml/L dilution)",
            "sprayer_tanks_15L": round(water_volume_liters / 15.0, 1),
            "safety_equipment": ["Gloves", "Basic eye protection"]
        }
        
    if "early blight" in disease.lower():
        chem_mass_g = round(water_volume_liters * 2.5, 1) # 2.5 g/L Mancozeb
        neem_ml = round(water_volume_liters * 5.0, 1) # 5 ml/L Neem
        chem_name = f"Mancozeb 75% WP: {round(chem_mass_g/1000, 2)} kg (or Azoxystrobin: {round(water_volume_liters * 1.0, 1)} ml)"
        org_name = f"Pure Neem Oil: {round(neem_ml/1000, 2)} L + Trichoderma: {round(water_volume_liters * 5 / 1000, 2)} kg"
    elif "late blight" in disease.lower():
        chem_mass_g = round(water_volume_liters * 2.5, 1) # 2.5 g/L Metalaxyl+Mancozeb
        chem_name = f"Ridomil MZ (Metalaxyl+Mancozeb): {round(chem_mass_g/1000, 2)} kg"
        org_name = f"Copper Hydroxide: {round(water_volume_liters * 2.0 / 1000, 2)} kg"
    elif "rust" in disease.lower():
        chem_name = f"Propiconazole 25% EC: {round(water_volume_liters * 1.0, 1)} ml"
        org_name = f"Wettable Sulfur 80% WP: {round(water_volume_liters * 3.0 / 1000, 2)} kg"
    elif "bacterial spot" in disease.lower():
        chem_name = f"Copper Oxychloride (50% WP): {round(water_volume_liters * 2.5 / 1000, 2)} kg + Streptocycline: {round(water_volume_liters * 0.05, 1)} g"
        org_name = f"Bacillus subtilis bio-agent: {round(water_volume_liters * 2.5 / 1000, 2)} kg"
    else:
        chem_name = f"Mancozeb 75% WP: {round(water_volume_liters * 2.5 / 1000, 2)} kg"
        org_name = f"Neem formulation (10,000 ppm): {round(water_volume_liters * 3.0 / 1000, 2)} L"
        
    return {
        "crop": crop,
        "condition": disease,
        "field_area_acres": area_acres,
        "water_volume_liters": water_volume_liters,
        "chemical_required": chem_name,
        "organic_required": org_name,
        "sprayer_tanks_15L": round(water_volume_liters / 15.0, 1),
        "safety_equipment": ["N95 / Chemical Mask", "Nitrile Gloves", "Protective Goggles", "Boots"]
    }

