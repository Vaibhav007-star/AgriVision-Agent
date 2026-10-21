"""
AgriVision Agent — Haryana Agricultural Schemes & CCS HAU Packages Knowledge Base (Pillar 5)
Provides grounded retrieval for state agricultural subsidies, crop diversification incentives,
seed varieties, and crop insurance policies.
"""

from typing import Dict, Any, List, Optional
import re


HARYANA_GOVERNMENT_SCHEMES = [
    {
        "id": "bhavantar_bharpai",
        "title": "भावांतर भरपाई योजना (Bhavantar Bharpai Yojana - BBY)",
        "department": "Department of Agriculture & Farmers Welfare, Haryana",
        "beneficiaries": "Haryana Vegetable & Fruit Farmers (Horticulture)",
        "keywords": ["भावांतर", "भरपाई", "bhavantar", "bby", "loss", "mandi price fall", "base price"],
        "eligibility": "Farmers registered on Meri Fasal Mera Byora (MFMB) portal cultivating scheduled crops (Tomato, Potato, Onion, Cauliflower, Carrot, Peas, Guava, Kinnow, etc.).",
        "protected_base_prices": {
            "Tomato": "₹400 / Quintal",
            "Potato": "₹400 / Quintal",
            "Onion": "₹500 / Quintal",
            "Cauliflower": "₹500 / Quintal"
        },
        "benefits": "If wholesale APMC market price drops below protected baseline price, the state government compensates the exact difference directly into the farmer's DBT bank account.",
        "documents": ["Meri Fasal Mera Byora (MFMB) Registration ID", "Aadhaar Card", "Bank Passbook", "Parivar Pehchan Patra (PPP)"],
        "portal_url": "https://fasal.haryana.gov.in"
    },
    {
        "id": "mera_pani_meri_virasat",
        "title": "मेरा पानी मेरी विरासत (Mera Pani Meri Virasat - MPMV)",
        "department": "Haryana Water Resources & Agriculture Department",
        "beneficiaries": "Paddy (Dhan) cultivating farmers in dark zones / critical groundwater blocks",
        "keywords": ["पानी", "विरासत", "mera pani", "mpmv", "paddy diversification", "groundwater", "subsidy 7000"],
        "eligibility": "Farmers replacing water-intensive paddy with alternative low-water crops (Maize, Cotton, Pulses, Mustard, Vegetables, Fodder) or adopting Direct Seeded Rice (DSR).",
        "benefits": "Financial assistance of ₹7,000 per acre paid directly into the farmer's verified bank account for diversifying away from paddy.",
        "documents": ["MFMB Registration", "Aadhaar Card", "Land Jamabandi", "Bank Account linked to Aadhaar"],
        "portal_url": "https://fasal.haryana.gov.in"
    },
    {
        "id": "pm_kusum_solar",
        "title": "पीएम-कुसुम सोलर पंप योजना (PM-KUSUM Haryana Solar Water Pump Scheme)",
        "department": "New & Renewable Energy Department Haryana (HAREDA)",
        "beneficiaries": "Small, marginal, and off-grid farmers requiring irrigation",
        "keywords": ["कुसुम", "सोलर", "पंप", "kusum", "solar pump", "tubewell", "hareda", "subsidy 75"],
        "eligibility": "Farmers having agricultural land with micro-irrigation (Drip/Sprinkler) installed or committed, lacking grid electric connection.",
        "benefits": "Up to 75% capital subsidy on standalone Solar Photovoltaic Water Pumping Systems (3 HP, 5 HP, 7.5 HP, 10 HP AC/DC submersible/surface pumps). Farmer pays only 25%.",
        "documents": ["Parivar Pehchan Patra (PPP)", "Land Ownership Farad / Jamabandi", "Micro Irrigation Certificate", "Bank Passbook"],
        "portal_url": "https://saralharyana.gov.in"
    },
    {
        "id": "pmfby_crop_insurance",
        "title": "प्रधानमंत्री फसल बीमा योजना (PMFBY Haryana)",
        "department": "Ministry of Agriculture & Farmers Welfare",
        "beneficiaries": "All Haryana loanee and non-loanee farmers cultivating notified food crops & oilseeds",
        "keywords": ["बीमा", "फसल बीमा", "pmfby", "crop insurance", "claim", "damage compensation"],
        "eligibility": "Registered farmers in notified clusters. Premium rates capped at 1.5% for Rabi (Wheat, Mustard, Barley, Gram), 2.0% for Kharif (Paddy, Cotton, Bajra), and 5% for commercial/horticultural crops.",
        "benefits": "Full sum insured compensation for prevented sowing, mid-season localized adversity (hailstorm, cloudburst, inundation), and post-harvest unseasonal rain damages within 72 hours intimation.",
        "documents": ["Crop Sowing Certificate / Patwari Girdawari", "Aadhaar Card", "Bank Account", "Land Possession Proof"],
        "portal_url": "https://pmfby.gov.in"
    }
]

CCS_HAU_RECOMMENDED_VARIETIES = {
    "wheat": {
        "crop": "Wheat (कनक / गेहूं)",
        "varieties": [
            {"code": "WH-1105", "features": "Timely sown irrigated; high resistance to yellow and brown rust; yield 22-24 Q/acre."},
            {"code": "HD-2967", "features": "Broadly adapted across all Haryana zones; tolerant to terminal heat; yield 21-23 Q/acre."},
            {"code": "WH-1184", "features": "Excellent chapati quality; resistant to stripe rust pustules; recommended for Karnal, Kurukshetra, Ambala."},
            {"code": "PBW-725", "features": "Newer rust resistant variety; robust lodging resistance in heavy alluvial soil."}
        ]
    },
    "paddy": {
        "crop": "Paddy / Rice (धान / बासमती)",
        "varieties": [
            {"code": "Pusa Basmati 1121", "features": "World famous extra-long slender grain; premium mandi export price; 140 days duration."},
            {"code": "Pusa Basmati 1509", "features": "Early maturing (115-120 days); saves 3-4 irrigations; ideal before potato/vegetables."},
            {"code": "Pusa Basmati 1847", "features": "Improved 1509 with dual genes resistant to Bacterial Leaf Blight and Blast."}
        ]
    },
    "mustard": {
        "crop": "Mustard (सरसों / राई)",
        "varieties": [
            {"code": "RH-725", "features": "High oil content (40%); bold seeds; resistant to white rust; average yield 10-12 Q/acre."},
            {"code": "RH-749", "features": "Recommended for entire Haryana irrigated belt; tolerant to frost and alternaria blight."}
        ]
    }
}


def search_schemes_and_packages(query: str) -> Dict[str, Any]:
    """
    Retrieves matching Haryana agricultural government schemes or
    CCS HAU crop packages based on natural language query.
    """
    q_clean = query.lower().strip()
    matched_schemes = []

    for s in HARYANA_GOVERNMENT_SCHEMES:
        for kw in s["keywords"]:
            if kw in q_clean or s["id"] in q_clean:
                matched_schemes.append(s)
                break

    # Check crop variety query
    matched_variety = None
    for crop_key, v_data in CCS_HAU_RECOMMENDED_VARIETIES.items():
        if crop_key in q_clean or any(v["code"].lower() in q_clean for v in v_data["varieties"]):
            matched_variety = v_data
            break

    if not matched_schemes and not matched_variety:
        # Return all active major schemes by default
        return {
            "status": "ALL_SCHEMES",
            "query": query,
            "total_schemes": len(HARYANA_GOVERNMENT_SCHEMES),
            "schemes": HARYANA_GOVERNMENT_SCHEMES,
            "recommended_varieties": CCS_HAU_RECOMMENDED_VARIETIES
        }

    return {
        "status": "MATCHED",
        "query": query,
        "matched_schemes": matched_schemes,
        "recommended_varieties": matched_variety
    }
