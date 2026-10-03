"""
Disease Pathology Tool (app/agent/tools/disease_info_tool.py).
Provides symptoms, causal pathogen, and integrated management strategies.
"""

from typing import Dict, Any

DISEASE_DATABASE = {
    "Early Blight": {
        "causal_agent": "Alternaria solani (Fungus)",
        "symptoms": "Concentric dark brown rings ('target board' / bullseye pattern) on older lower leaves, surrounded by chlorotic yellow halos.",
        "primary_conditions": "Warm temperatures (24-29°C) with alternating wet and dry periods.",
        "management": "Copper fungicides, Mancozeb 75% WP, 3-year crop rotation."
    },
    "Late Blight": {
        "causal_agent": "Phytophthora infestans (Oomycete)",
        "symptoms": "Irregular water-soaked greasy lesions turning dark brown to purplish-black, with white fungal sporulation under the leaf surface in humid weather.",
        "primary_conditions": "Cool, humid weather (15-20°C, RH > 90%). Rapidly destructive.",
        "management": "Ridomil Gold, Cymoxanil + Mancozeb, immediate removal of infected vines."
    },
    "Common Rust": {
        "causal_agent": "Puccinia sorghi (Fungus)",
        "symptoms": "Small, powdery golden-brown to cinnamon pustules appearing on both upper and lower leaf surfaces.",
        "primary_conditions": "High humidity (RH > 95%) with moderate temperatures (16-25°C).",
        "management": "Azoxystrobin, Propiconazole, resistant hybrids."
    },
    "Healthy": {
        "causal_agent": "None (Non-pathogenic)",
        "symptoms": "Uniform green pigmentation, intact leaf margins, active photosynthesis.",
        "primary_conditions": "Balanced soil nutrition and moisture.",
        "management": "Preventive bio-stimulants (Neem oil 3ml/L every 25 days)."
    }
}


def get_disease_info(crop_name: str, disease_name: str) -> Dict[str, Any]:
    """Retrieves diagnostic profile for the target crop disease."""
    for key, data in DISEASE_DATABASE.items():
        if key.lower() in disease_name.lower():
            return {"found": True, "disease": key, "crop": crop_name, **data}
    return {
        "found": False,
        "disease": disease_name,
        "crop": crop_name,
        "causal_agent": "Foliar Plant Pathogen",
        "symptoms": "Visual leaf discoloration, spots, or blighting.",
        "primary_conditions": "Foliar leaf wetness and microclimate humidity.",
        "management": "Broad-spectrum contact protectant fungicides and sanitation."
    }

