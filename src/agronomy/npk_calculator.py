"""
AgriVision Agent — N-P-K Soil Nutrition & Deficiency Calculator
Grounded in CCS HAU Hisar Package of Practices for Soil Fertility & Plant Nutrition.
Calculates exact chemical fertilizer bag requirements and bio-fertilizer alternatives
based on acreage, crop, growth stage, soil texture, and visual deficiency symptoms.
"""

from typing import Dict, Any, List, Optional
import math


# ============================================================================
# Standard Regional Fertilizer Baselines (kg/acre pure N:P2O5:K2O)
# Based on CCS Haryana Agricultural University (HAU) Hisar Standards
# ============================================================================

CROP_NPK_STANDARDS: Dict[str, Dict[str, Any]] = {
    "wheat": {
        "crop_name": "Wheat (कनक / गेहूं)",
        "pure_n_kg_acre": 60.0,
        "pure_p_kg_acre": 25.0,
        "pure_k_kg_acre": 15.0,
        "zinc_kg_acre": 10.0,
        "splits": {
            "basal": {"n_pct": 0.50, "p_pct": 1.0, "k_pct": 1.0, "zn_pct": 1.0},
            "first_irrigation": {"n_pct": 0.25, "p_pct": 0.0, "k_pct": 0.0, "zn_pct": 0.0},
            "second_irrigation": {"n_pct": 0.25, "p_pct": 0.0, "k_pct": 0.0, "zn_pct": 0.0}
        }
    },
    "paddy": {
        "crop_name": "Paddy / Rice (धान / बासमती)",
        "pure_n_kg_acre": 50.0,
        "pure_p_kg_acre": 20.0,
        "pure_k_kg_acre": 20.0,
        "zinc_kg_acre": 10.0,
        "splits": {
            "basal": {"n_pct": 0.33, "p_pct": 1.0, "k_pct": 1.0, "zn_pct": 1.0},
            "tillering": {"n_pct": 0.33, "p_pct": 0.0, "k_pct": 0.0, "zn_pct": 0.0},
            "panicle_initiation": {"n_pct": 0.34, "p_pct": 0.0, "k_pct": 0.0, "zn_pct": 0.0}
        }
    },
    "cotton": {
        "crop_name": "Cotton / Bt Cotton (नरमा / कपास)",
        "pure_n_kg_acre": 70.0,
        "pure_p_kg_acre": 25.0,
        "pure_k_kg_acre": 25.0,
        "zinc_kg_acre": 10.0,
        "splits": {
            "basal": {"n_pct": 0.33, "p_pct": 1.0, "k_pct": 1.0, "zn_pct": 1.0},
            "squaring": {"n_pct": 0.33, "p_pct": 0.0, "k_pct": 0.0, "zn_pct": 0.0},
            "flowering_boll": {"n_pct": 0.34, "p_pct": 0.0, "k_pct": 0.0, "zn_pct": 0.0}
        }
    },
    "mustard": {
        "crop_name": "Mustard / Raya (सरसों / राई)",
        "pure_n_kg_acre": 35.0,
        "pure_p_kg_acre": 15.0,
        "pure_k_kg_acre": 10.0,
        "zinc_kg_acre": 5.0,
        "splits": {
            "basal": {"n_pct": 0.60, "p_pct": 1.0, "k_pct": 1.0, "zn_pct": 1.0},
            "first_irrigation": {"n_pct": 0.40, "p_pct": 0.0, "k_pct": 0.0, "zn_pct": 0.0}
        }
    },
    "sugarcane": {
        "crop_name": "Sugarcane (गन्ना)",
        "pure_n_kg_acre": 100.0,
        "pure_p_kg_acre": 30.0,
        "pure_k_kg_acre": 30.0,
        "zinc_kg_acre": 10.0,
        "splits": {
            "basal": {"n_pct": 0.33, "p_pct": 1.0, "k_pct": 1.0, "zn_pct": 1.0},
            "tillering": {"n_pct": 0.33, "p_pct": 0.0, "k_pct": 0.0, "zn_pct": 0.0},
            "monsoon_start": {"n_pct": 0.34, "p_pct": 0.0, "k_pct": 0.0, "zn_pct": 0.0}
        }
    },
    "tomato": {
        "crop_name": "Tomato (टमाटर)",
        "pure_n_kg_acre": 50.0,
        "pure_p_kg_acre": 25.0,
        "pure_k_kg_acre": 25.0,
        "zinc_kg_acre": 5.0,
        "splits": {
            "basal": {"n_pct": 0.40, "p_pct": 1.0, "k_pct": 1.0, "zn_pct": 1.0},
            "vegetative": {"n_pct": 0.30, "p_pct": 0.0, "k_pct": 0.0, "zn_pct": 0.0},
            "fruit_set": {"n_pct": 0.30, "p_pct": 0.0, "k_pct": 0.0, "zn_pct": 0.0}
        }
    },
    "potato": {
        "crop_name": "Potato (आलू)",
        "pure_n_kg_acre": 65.0,
        "pure_p_kg_acre": 30.0,
        "pure_k_kg_acre": 40.0,
        "zinc_kg_acre": 10.0,
        "splits": {
            "basal": {"n_pct": 0.50, "p_pct": 1.0, "k_pct": 1.0, "zn_pct": 1.0},
            "earthing_up": {"n_pct": 0.50, "p_pct": 0.0, "k_pct": 0.0, "zn_pct": 0.0}
        }
    }
}

# Soil texture modifiers based on Haryana regional soils
SOIL_TYPE_MODIFIERS: Dict[str, Dict[str, float]] = {
    "alluvial_loam": {"label": "Alluvial Loamy (Karnal, Kurukshetra, Ambala)", "n_factor": 1.0, "p_factor": 1.0, "k_factor": 1.0},
    "sandy_loam": {"label": "Sandy Loam (Hisar, Jind, Rohtak)", "n_factor": 1.10, "p_factor": 1.0, "k_factor": 1.05},
    "light_sandy": {"label": "Light Sandy / Arid (Sirsa, Bhiwani, Mahendragarh)", "n_factor": 1.20, "p_factor": 1.05, "k_factor": 1.15},
    "clayey_lowland": {"label": "Clayey Heavy (Yamuna / Ghaggar floodplains)", "n_factor": 0.95, "p_factor": 0.95, "k_factor": 1.0}
}

# Visual Nutrient Deficiency Diagnostic Guide
NUTRIENT_DEFICIENCY_GUIDE = {
    "nitrogen": {
        "element": "Nitrogen (N) Deficiency",
        "vernacular_name": "नाइट्रोजन की कमी (पीलापन)",
        "symptoms": "Oldest lower leaves turn pale yellow starting from the leaf tip in a characteristic V-shape along the midrib. Plant growth is severely stunted with thin stems.",
        "distinction_from_pathology": "Affects entire lowest leaves symmetrically along the midrib without fungal powder or water-soaked halos.",
        "emergency_spray": "Foliar spray of 2% Urea solution (2 kg Urea in 100 L water per acre) for quick absorption within 48 hours."
    },
    "phosphorus": {
        "element": "Phosphorus (P) Deficiency",
        "vernacular_name": "फॉस्फोरस की कमी (बैंगनी पत्तियां)",
        "symptoms": "Leaves turn dark green and develop intense purple or bronze pigmentation along the undersides and margins. Root growth is stunted with delayed maturity.",
        "distinction_from_pathology": "Uniform purplish tinge on leaf underside without necrotic center or leaf spots.",
        "emergency_spray": "Foliar spray of 1% DAP solution (1 kg dissolved DAP in 100 L water per acre)."
    },
    "potassium": {
        "element": "Potassium (K) Deficiency",
        "vernacular_name": "पोटाश की कमी (पत्तियों का किनारा जलना)",
        "symptoms": "Marginal scorching and chlorosis of older leaves. Leaf margins appear burnt or 'fired'. Stems become weak and susceptible to lodging.",
        "distinction_from_pathology": "Symmetrical edge firing without fungal spore pustules.",
        "emergency_spray": "Foliar spray of 1.5% Potassium Nitrate (13-0-45) @ 1.5 kg in 100 L water per acre."
    },
    "zinc": {
        "element": "Zinc (Zn) Deficiency",
        "vernacular_name": "जिंक की कमी (खैरा रोग)",
        "symptoms": "Interveinal chlorosis on middle leaves. In rice, causes classic 'Khaira disease' with rusty brown spots on lower leaves appearing 2-3 weeks after transplanting.",
        "distinction_from_pathology": "Rusty spots coalesce into bronzed leaves across entire localized patches in the field.",
        "emergency_spray": "Spray 0.5% Zinc Sulphate (21%) @ 1.0 kg + 0.5 kg unslaked lime in 200 L water per acre."
    },
    "iron": {
        "element": "Iron (Fe) Deficiency",
        "vernacular_name": "लोहा तत्व की कमी (सफेद पत्तियां)",
        "symptoms": "Severe interveinal chlorosis on youngest top leaves. Leaf blade turns ivory white while veins remain thin and green.",
        "distinction_from_pathology": "Affects strictly the top new leaves in alkaline/calcareous soils without dead spots.",
        "emergency_spray": "Spray 1% Ferrous Sulphate @ 1 kg + 100 g citric acid in 100 L water per acre."
    }
}


def calculate_fertilizer_dosage(
    crop_name: str,
    acres: float = 1.0,
    soil_type: str = "alluvial_loam",
    growth_stage: str = "basal",
    deficiency_observed: Optional[str] = None
) -> Dict[str, Any]:
    """
    Computes exact chemical bag requirements and bio-fertilizer alternatives
    for a given crop acreage based on CCS HAU Hisar soil science baselines.
    """
    key = crop_name.lower().strip()
    if key not in CROP_NPK_STANDARDS:
        key = "wheat"

    crop_data = CROP_NPK_STANDARDS[key]
    soil_mod = SOIL_TYPE_MODIFIERS.get(soil_type, SOIL_TYPE_MODIFIERS["alluvial_loam"])

    # 1. Calculate pure nutrient requirements
    tot_pure_n = crop_data["pure_n_kg_acre"] * acres * soil_mod["n_factor"]
    tot_pure_p = crop_data["pure_p_kg_acre"] * acres * soil_mod["p_factor"]
    tot_pure_k = crop_data["pure_k_kg_acre"] * acres * soil_mod["k_factor"]
    tot_zinc = crop_data["zinc_kg_acre"] * acres

    # 2. Stage split factors
    stage_key = growth_stage.lower().strip()
    splits = crop_data["splits"]
    if stage_key not in splits:
        stage_key = list(splits.keys())[0]

    stage_ratios = splits[stage_key]
    req_n = tot_pure_n * stage_ratios["n_pct"]
    req_p = tot_pure_p * stage_ratios["p_pct"]
    req_k = tot_pure_k * stage_ratios["k_pct"]
    req_zn = tot_zinc * stage_ratios.get("zn_pct", 0.0)

    # 3. Fertilizer Formulation:
    # Option 1: DAP (18:46:0) + Urea (46% N) + MOP (60% K2O)
    # 50kg bag of DAP provides 9kg N and 23kg P2O5
    dap_bags_50kg = round((req_p / 23.0), 1) if req_p > 0 else 0.0
    n_from_dap = dap_bags_50kg * 9.0
    remaining_n = max(0.0, req_n - n_from_dap)
    # 45kg bag of Urea provides 20.7kg N (46%)
    urea_bags_45kg = round((remaining_n / 20.7), 1) if remaining_n > 0 else 0.0
    # 50kg bag of MOP provides 30kg K2O (60%)
    mop_bags_50kg = round((req_k / 30.0), 1) if req_k > 0 else 0.0
    zinc_kg = round(req_zn, 1)

    # Bio-fertilizer equivalents
    vermicompost_tonnes = round(acres * 1.5, 1)
    azotobacter_packets = math.ceil(acres * 2)
    psb_packets = math.ceil(acres * 2)

    # Deficiency advisory if provided
    deficiency_info = None
    if deficiency_observed and deficiency_observed.lower() in NUTRIENT_DEFICIENCY_GUIDE:
        deficiency_info = NUTRIENT_DEFICIENCY_GUIDE[deficiency_observed.lower()]

    return {
        "status": "SUCCESS",
        "crop": crop_data["crop_name"],
        "acres": acres,
        "soil_type": soil_mod["label"],
        "growth_stage": stage_key.replace("_", " ").title(),
        "pure_nutrients_kg": {
            "nitrogen_n": round(req_n, 1),
            "phosphorus_p2o5": round(req_p, 1),
            "potassium_k2o": round(req_k, 1),
            "zinc_zn": round(req_zn, 1)
        },
        "chemical_bags_needed": {
            "urea_45kg_bags": urea_bags_45kg,
            "dap_50kg_bags": dap_bags_50kg,
            "mop_potash_50kg_bags": mop_bags_50kg,
            "zinc_sulphate_kg": zinc_kg
        },
        "organic_alternatives": {
            "vermicompost_tonnes": vermicompost_tonnes,
            "azotobacter_bio_fertilizer_pkts": azotobacter_packets,
            "psb_phosphate_solubilizing_pkts": psb_packets,
            "neem_cake_kg": round(acres * 100.0, 1)
        },
        "deficiency_triage": deficiency_info,
        "standard_schedule_summary": f"HAU Hisar schedule for {acres} acres {crop_data['crop_name']}: Apply {dap_bags_50kg} bags DAP and {mop_bags_50kg} bags MOP at sowing, with {urea_bags_45kg} bags Urea in scheduled splits."
    }
