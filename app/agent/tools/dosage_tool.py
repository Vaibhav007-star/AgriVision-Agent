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
        
    crop_l = crop.lower()
    dis_l = disease.lower()
    
    # Crop & Disease Specific Calibration:
    if "wheat" in crop_l and ("rust" in dis_l or "stripe" in dis_l or "yellow" in dis_l):
        # CCS HAU Hisar / ICAR Recommendation: Propiconazole 25% EC (Tilt) @ 1.0 ml per Liter (200 ml / acre in 200 L water)
        prop_ml = round(field_acres * 200.0, 0)
        chem_str = f"{prop_ml:.0f} ml of Propiconazole 25% EC (Tilt) @ 1 ml/L ({prop_ml/1000.0:.2f} L in {water_volume_liters:.0f} L water)"
    elif "rice" in crop_l and ("bacterial" in dis_l or "blight" in dis_l):
        # Streptocycline (20 g / acre) + Copper Oxychloride 50% WP (500 g / acre)
        strep_g = round(field_acres * 20.0, 0)
        coc_g = round(field_acres * 500.0, 0)
        chem_str = f"{strep_g:.0f} g of Streptocycline + {coc_g:.0f} g of Copper Oxychloride 50% WP in {water_volume_liters:.0f} L water"
    elif "cotton" in crop_l and ("diseased" in dis_l or "bacterial" in dis_l):
        strep_g = round(field_acres * 20.0, 0)
        coc_g = round(field_acres * 500.0, 0)
        chem_str = f"{strep_g:.0f} g Streptocycline + {coc_g:.0f} g Copper Oxychloride 50% WP in {water_volume_liters:.0f} L water"
    elif "sugarcane" in crop_l and "red" in dis_l:
        carb_g = round(field_acres * 200.0, 0)
        chem_str = f"{carb_g:.0f} g Carbendazim 50% WP Sett Treatment + Trichoderma harzianum @ 10 kg/acre soil application"
    elif "late" in dis_l:
        # Late blight: Cymoxanil + Mancozeb (Curzate) @ 3 g/L
        chem_grams = round(water_volume_liters * 3.0, 1)
        chem_kg = chem_grams / 1000.0
        chem_str = f"{chem_kg:.2f} kg ({chem_grams:.0f} g) of Cymoxanil 8% + Mancozeb 64% WP (Curzate)"
    else:
        # Standard contact fungicide rate: 2.5 grams per Liter
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

