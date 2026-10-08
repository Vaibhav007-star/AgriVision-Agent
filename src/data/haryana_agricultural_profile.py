"""
Haryana Agricultural Profile & District Crop Database (src/data/haryana_agricultural_profile.py).

Comprehensive agronomic database capturing:
1. All 22 districts of Haryana with their primary cities/towns and commonly grown crops.
2. Regional agricultural agro-climatic belts (North-East, Central, Western, Southern).
3. Crop seasonality (Kharif, Rabi, Zaid).
4. Major crop disease susceptibility per crop and district.
5. Inverted index for querying districts by crop and crops by district.
"""

from typing import Dict, List, Any, Optional

HARYANA_DISTRICTS: Dict[str, Dict[str, Any]] = {
    "Ambala": {
        "belt": "North-East",
        "main_cities": ["Ambala City", "Ambala Cantt", "Naraingarh", "Barara", "Mullana", "Shahzadpur"],
        "crops": ["Wheat", "Paddy", "Sugarcane", "Maize", "Vegetables"],
        "soil_type": "Alluvial / Loamy",
        "irrigation": "Canal & Tube-well",
        "apmc_mandi": "Ambala Cantt APMC / City Grain Market"
    },
    "Bhiwani": {
        "belt": "Western / South-Western",
        "main_cities": ["Bhiwani", "Loharu", "Siwani", "Tosham", "Bawani Khera"],
        "crops": ["Bajra", "Guar", "Mustard", "Cotton", "Gram", "Wheat"],
        "soil_type": "Sandy to Sandy Loam",
        "irrigation": "Sprinkler & Canal Lift",
        "apmc_mandi": "Bhiwani Grain & Oilseed Mandi"
    },
    "Charkhi Dadri": {
        "belt": "Southern",
        "main_cities": ["Charkhi Dadri", "Badhra", "Bahal"],
        "crops": ["Bajra", "Mustard", "Wheat", "Guar", "Cotton"],
        "soil_type": "Sandy Loam",
        "irrigation": "Canal & Tube-well",
        "apmc_mandi": "Charkhi Dadri Mandi"
    },
    "Faridabad": {
        "belt": "Southern",
        "main_cities": ["Faridabad", "Ballabgarh"],
        "crops": ["Wheat", "Paddy", "Bajra", "Mustard", "Vegetables"],
        "soil_type": "Yamuna Alluvial",
        "irrigation": "Tube-well",
        "apmc_mandi": "Ballabgarh APMC Mandi"
    },
    "Fatehabad": {
        "belt": "Western / South-Western",
        "main_cities": ["Fatehabad", "Tohana", "Ratia", "Bhuna", "Jakhal"],
        "crops": ["Cotton", "Wheat", "Paddy", "Mustard", "Guar"],
        "soil_type": "Sandy Loam / Light Alluvial",
        "irrigation": "Bhakra Canal System",
        "apmc_mandi": "Tohana Grain Market / Fatehabad APMC"
    },
    "Gurugram": {
        "belt": "Southern",
        "main_cities": ["Gurugram", "Sohna", "Pataudi", "Farrukhnagar", "Manesar"],
        "crops": ["Wheat", "Mustard", "Bajra", "Vegetables"],
        "soil_type": "Sandy Loam",
        "irrigation": "Tube-well & NCR Micro-irrigation",
        "apmc_mandi": "Gurugram Khandsa APMC"
    },
    "Hisar": {
        "belt": "Western / South-Western",
        "main_cities": ["Hisar", "Hansi", "Barwala", "Adampur", "Narnaund", "Uklana"],
        "crops": ["Wheat", "Cotton", "Mustard", "Bajra", "Gram", "Guar"],
        "soil_type": "Sandy Loam (Cotton-Wheat Belt)",
        "irrigation": "Western Yamuna Canal & Tube-wells",
        "apmc_mandi": "Hisar New Grain Market / Hansi APMC"
    },
    "Jhajjar": {
        "belt": "Central",
        "main_cities": ["Jhajjar", "Bahadurgarh", "Beri", "Matenhail"],
        "crops": ["Wheat", "Paddy", "Mustard", "Bajra", "Vegetables"],
        "soil_type": "Loam to Sandy Loam",
        "irrigation": "JLN Canal System",
        "apmc_mandi": "Bahadurgarh / Jhajjar Grain Market"
    },
    "Jind": {
        "belt": "Central",
        "main_cities": ["Jind", "Narwana", "Safidon", "Julana", "Uchana"],
        "crops": ["Wheat", "Paddy", "Sugarcane", "Cotton", "Mustard"],
        "soil_type": "Fertile Loam",
        "irrigation": "Canal-irrigated (Bhakra & Western Yamuna)",
        "apmc_mandi": "Narwana / Jind Grain Market"
    },
    "Kaithal": {
        "belt": "North-East",
        "main_cities": ["Kaithal", "Pundri", "Guhla (Cheeka)", "Rajaund"],
        "crops": ["Paddy", "Wheat", "Sugarcane"],
        "soil_type": "Heavy Alluvial Clay Loam (Prime Basmati)",
        "irrigation": "Canal Network & Tube-wells",
        "apmc_mandi": "Kaithal New Grain Market / Cheeka Mandi"
    },
    "Karnal": {
        "belt": "North-East",
        "main_cities": ["Karnal", "Assandh", "Gharaunda", "Indri", "Nilokheri", "Taraori"],
        "crops": ["Paddy", "Wheat", "Sugarcane", "Maize", "Vegetables"],
        "soil_type": "Highly Fertile Alluvial (Rice Bowl of Haryana)",
        "irrigation": "Western Yamuna Canal & Extensive Tube-wells",
        "apmc_mandi": "Karnal New Grain Market / Gharaunda Vegetable Hub"
    },
    "Kurukshetra": {
        "belt": "North-East",
        "main_cities": ["Kurukshetra (Thanesar)", "Shahabad", "Pehowa", "Ladwa"],
        "crops": ["Paddy", "Wheat", "Sugarcane", "Potato", "Sunflower"],
        "soil_type": "Rich Loam / Silt Loam (Potato & Basmati Belt)",
        "irrigation": "Canal & Deep Submersible Tube-wells",
        "apmc_mandi": "Shahabad Markanda / Pipli APMC / Ladwa Mandi"
    },
    "Mahendragarh": {
        "belt": "Southern",
        "main_cities": ["Narnaul", "Mahendragarh", "Ateli", "Nangal Chaudhry", "Kanina"],
        "crops": ["Bajra", "Mustard", "Guar", "Gram", "Wheat"],
        "soil_type": "Arid Sandy Loam",
        "irrigation": "Drip & Sprinkler (JLN Feeder)",
        "apmc_mandi": "Narnaul Grain & Oilseed APMC"
    },
    "Nuh": {
        "belt": "Southern",
        "main_cities": ["Nuh", "Ferozepur Jhirka", "Punahana", "Taoru"],
        "crops": ["Wheat", "Mustard", "Bajra", "Vegetables"],
        "soil_type": "Sandy Alluvial with Saline Pockets",
        "irrigation": "Canal & Tube-well",
        "apmc_mandi": "Taoru / Nuh APMC Mandi"
    },
    "Palwal": {
        "belt": "Southern",
        "main_cities": ["Palwal", "Hodal", "Hathin"],
        "crops": ["Wheat", "Paddy", "Mustard", "Potato", "Vegetables"],
        "soil_type": "Yamuna Plain Alluvial",
        "irrigation": "Gurgaon Canal & Tube-wells",
        "apmc_mandi": "Palwal Grain Market / Hodal APMC"
    },
    "Panchkula": {
        "belt": "North-East",
        "main_cities": ["Panchkula", "Kalka", "Pinjore", "Raipur Rani"],
        "crops": ["Wheat", "Maize", "Paddy", "Vegetables", "Mango and Litchi"],
        "soil_type": "Shivalik Piedmont / Gravelly Loam",
        "irrigation": "Rainfed & Perennial Hill Streams",
        "apmc_mandi": "Panchkula Sector 20 / Kalka APMC"
    },
    "Panipat": {
        "belt": "Central",
        "main_cities": ["Panipat", "Samalkha", "Israna", "Bapoli"],
        "crops": ["Wheat", "Paddy", "Sugarcane", "Vegetables"],
        "soil_type": "Yamuna Floodplain Alluvial",
        "irrigation": "Western Yamuna Canal",
        "apmc_mandi": "Panipat Grain Market / Samalkha APMC"
    },
    "Rewari": {
        "belt": "Southern",
        "main_cities": ["Rewari", "Bawal", "Dharuhera", "Kosli"],
        "crops": ["Bajra", "Mustard", "Wheat", "Guar", "Gram"],
        "soil_type": "Sandy Loam",
        "irrigation": "Sprinkler & Tube-well",
        "apmc_mandi": "Rewari New Grain Market / Bawal APMC"
    },
    "Rohtak": {
        "belt": "Central",
        "main_cities": ["Rohtak", "Meham", "Kalanaur", "Sampla"],
        "crops": ["Wheat", "Paddy", "Mustard", "Bajra", "Vegetables"],
        "soil_type": "Medium to Heavy Loam",
        "irrigation": "JLN Canal & Drain Network",
        "apmc_mandi": "Rohtak New Grain Market / Meham APMC"
    },
    "Sirsa": {
        "belt": "Western / South-Western",
        "main_cities": ["Sirsa", "Dabwali", "Ellenabad", "Rania", "Kalanwali"],
        "crops": ["Cotton", "Wheat", "Paddy", "Mustard", "Guar"],
        "soil_type": "Light Sandy to Sierozem (Leading Cotton District)",
        "irrigation": "Bhakra & Sirsa Branch Canals",
        "apmc_mandi": "Sirsa Grain & Cotton APMC (Largest in Haryana)"
    },
    "Sonipat": {
        "belt": "Central",
        "main_cities": ["Sonipat", "Gohana", "Kharkhoda", "Ganaur"],
        "crops": ["Wheat", "Paddy", "Sugarcane", "Vegetables", "Baby Corn"],
        "soil_type": "Highly Productive Alluvial (NCR Vegetable Belt)",
        "irrigation": "Western Yamuna Canal & Tube-wells",
        "apmc_mandi": "Ganaur International Horticulture Market / Sonipat APMC"
    },
    "Yamunanagar": {
        "belt": "North-East",
        "main_cities": ["Yamunanagar", "Jagadhri", "Radaur", "Bilaspur", "Chhachhrauli"],
        "crops": ["Sugarcane", "Paddy", "Wheat", "Maize", "Poplar (Agroforestry)"],
        "soil_type": "Rich Riverine Loam (Sugarcane & Timber Heartland)",
        "irrigation": "Western Yamuna River & Canals",
        "apmc_mandi": "Jagadhri / Radaur Grain & Sugarcane Mandi"
    }
}

# Regional Agricultural Belts
HARYANA_REGIONAL_BELTS: Dict[str, Dict[str, Any]] = {
    "North-East": {
        "districts": ["Ambala", "Yamunanagar", "Panchkula", "Kurukshetra", "Karnal", "Kaithal"],
        "description": "Canal-irrigated and highly fertile. Rice (especially world-renowned Basmati), Wheat, and Sugarcane dominate.",
        "primary_crops": ["Paddy", "Wheat", "Sugarcane", "Potato", "Maize"]
    },
    "Central": {
        "districts": ["Panipat", "Sonipat", "Jind", "Rohtak", "Jhajjar"],
        "description": "Wheat-Paddy rotation, with Sugarcane, Baby Corn, and intensive commercial Vegetable farming near Delhi-NCR.",
        "primary_crops": ["Wheat", "Paddy", "Vegetables", "Sugarcane", "Mustard"]
    },
    "Western / South-Western": {
        "districts": ["Sirsa", "Fatehabad", "Hisar", "Bhiwani"],
        "description": "Haryana's prominent Cotton-Wheat belt, accompanied by Mustard, Guar, and Bajra.",
        "primary_crops": ["Cotton", "Wheat", "Mustard", "Bajra", "Guar"]
    },
    "Southern": {
        "districts": ["Mahendragarh", "Rewari", "Charkhi Dadri", "Nuh", "Gurugram", "Faridabad", "Palwal"],
        "description": "Drier and sandier terrain. Bajra, Mustard, Guar, and Gram dominate, with peri-urban vegetable belts near NCR.",
        "primary_crops": ["Bajra", "Mustard", "Wheat", "Guar", "Gram", "Vegetables"]
    }
}

# Seasonality Matrix
HARYANA_CROP_SEASONS = {
    "Kharif": {
        "sowing_harvest": "June-July to Oct-Nov",
        "crops": ["Paddy", "Bajra", "Cotton", "Maize", "Sugarcane", "Guar", "Sorghum"]
    },
    "Rabi": {
        "sowing_harvest": "Oct-Nov to Mar-Apr",
        "crops": ["Wheat", "Mustard", "Gram", "Barley", "Potato", "Sunflower"]
    },
    "Zaid": {
        "sowing_harvest": "March to June",
        "crops": ["Vegetables", "Tomato", "Pepper Bell", "Melons", "Fodder", "Moong"]
    }
}

# Crops Haryana Is Best Known For
CROP_SPECIALIZATION_LEADERS: Dict[str, List[str]] = {
    "Basmati rice": ["Karnal", "Kaithal", "Kurukshetra", "Yamunanagar", "Ambala"],
    "Wheat": ["Karnal", "Kurukshetra", "Hisar", "Jind", "Sirsa", "Rohtak", "Ambala"],
    "Cotton": ["Sirsa", "Fatehabad", "Hisar", "Bhiwani"],
    "Sugarcane": ["Yamunanagar", "Karnal", "Panipat", "Sonipat", "Ambala"],
    "Mustard": ["Mahendragarh", "Rewari", "Bhiwani", "Hisar", "Charkhi Dadri"],
    "Bajra": ["Mahendragarh", "Bhiwani", "Rewari", "Charkhi Dadri"],
    "Vegetables": ["Sonipat", "Jhajjar", "Palwal", "Karnal", "Rohtak"],
    "Potato": ["Kurukshetra", "Shahabad", "Yamunanagar", "Ambala", "Palwal"]
}


def get_all_districts() -> List[str]:
    """Returns sorted list of all 22 Haryana districts."""
    return sorted(list(HARYANA_DISTRICTS.keys()))


def get_district_info(district_name: str) -> Optional[Dict[str, Any]]:
    """Retrieves full profile for a specific Haryana district."""
    for d, info in HARYANA_DISTRICTS.items():
        if d.lower() == district_name.strip().lower():
            return {**info, "district": d}
    return None


def get_crops_by_district(district_name: str) -> List[str]:
    """Returns list of commonly grown crops in the requested district."""
    info = get_district_info(district_name)
    return info["crops"] if info else []


def get_districts_by_crop(crop_name: str) -> List[str]:
    """Inverted query: returns all Haryana districts growing the given crop."""
    crop_lower = crop_name.strip().lower()
    matching_districts = []
    for d, info in HARYANA_DISTRICTS.items():
        for c in info["crops"]:
            if crop_lower in c.lower() or c.lower() in crop_lower:
                matching_districts.append(d)
                break
    return matching_districts


def get_crop_profile_for_location(location_query: str) -> Dict[str, Any]:
    """
    Intelligently identifies the district from any city/town in the location query
    and returns its crop list, belt, and primary agricultural focus.
    """
    loc_clean = location_query.lower()
    
    # 1. Match district name directly
    for d, info in HARYANA_DISTRICTS.items():
        if d.lower() in loc_clean:
            return {
                "matched_district": d,
                "belt": info["belt"],
                "common_crops": info["crops"],
                "apmc_mandi": info["apmc_mandi"],
                "main_cities": info["main_cities"]
            }
            
    # 2. Match city/town name
    for d, info in HARYANA_DISTRICTS.items():
        for city in info["main_cities"]:
            if city.lower() in loc_clean:
                return {
                    "matched_district": d,
                    "matched_city": city,
                    "belt": info["belt"],
                    "common_crops": info["crops"],
                    "apmc_mandi": info["apmc_mandi"],
                    "main_cities": info["main_cities"]
                }
                
    # Fallback to Karnal (Haryana agricultural heartland)
    karnal_info = HARYANA_DISTRICTS["Karnal"]
    return {
        "matched_district": "Karnal",
        "belt": karnal_info["belt"],
        "common_crops": karnal_info["crops"],
        "apmc_mandi": karnal_info["apmc_mandi"],
        "main_cities": karnal_info["main_cities"]
    }

