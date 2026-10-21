"""
Disease Pathology Tool (app/agent/tools/disease_info_tool.py).
Provides symptoms, causal pathogen, and integrated management strategies.
"""

from typing import Dict, Any

DISEASE_DATABASE = {
    "Stripe / Yellow Rust": {
        "causal_agent": "Puccinia striiformis f. sp. tritici (Fungus)",
        "symptoms": "Narrow, bright yellow to orange-yellow powdery pustules arranged in distinct linear stripes along wheat leaf veins.",
        "primary_conditions": "Cool temperatures (10-18°C) with persistent winter fog, dew, and drizzle (RH > 85%).",
        "management": "Propiconazole 25% EC (Tilt) @ 200 ml / 200 L water per acre, Tebuconazole 250 EC @ 200 ml / acre."
    },
    "Stripe Rust": {
        "causal_agent": "Puccinia striiformis f. sp. tritici (Fungus)",
        "symptoms": "Narrow, bright yellow to orange-yellow powdery pustules arranged in distinct linear stripes along wheat leaf veins.",
        "primary_conditions": "Cool temperatures (10-18°C) with persistent winter fog, dew, and drizzle (RH > 85%).",
        "management": "Propiconazole 25% EC (Tilt) @ 200 ml / 200 L water per acre, Tebuconazole 250 EC @ 200 ml / acre."
    },
    "Yellow Rust": {
        "causal_agent": "Puccinia striiformis f. sp. tritici (Fungus)",
        "symptoms": "Yellow powdery pustules in parallel rows along leaf blade veins on wheat.",
        "primary_conditions": "Cool temperatures (10-18°C) with morning dew/fog.",
        "management": "Propiconazole 25% EC (Tilt) @ 200 ml / 200 L water per acre."
    },
    "Leaf Rust": {
        "causal_agent": "Puccinia triticina (Fungus)",
        "symptoms": "Small, round to oval, scattered cinnamon-brown to orange-brown pustules predominantly on the upper leaf surface without linear striping.",
        "primary_conditions": "Moderate temperatures (18-25°C) with high humidity and morning dew.",
        "management": "Propiconazole 25% EC @ 200 ml / acre or Mancozeb 75% WP @ 500 g / acre in 200 L water."
    },
    "Stem Rust": {
        "causal_agent": "Puccinia graminis f. sp. tritici (Fungus)",
        "symptoms": "Elongated reddish-brown to black pustules rupturing leaf sheaths, stems, and glumes.",
        "primary_conditions": "Warm temperatures (20-30°C) with leaf moisture.",
        "management": "Propiconazole 25% EC @ 200 ml per acre in 200 L water."
    },
    "Bacterial Leaf Blight": {
        "causal_agent": "Xanthomonas oryzae pv. oryzae (Bacterium)",
        "symptoms": "Water-soaked yellowish undulating lesions on leaf margins of rice blades, developing into straw-colored bleached stripes with bacterial ooze beads.",
        "primary_conditions": "High humidity (> 75%) and temperatures 25-34°C with rain/winds.",
        "management": "Streptocycline @ 20 g + Copper Oxychloride 50% WP @ 500 g per acre in 200 L water."
    },
    "Brown Spot": {
        "causal_agent": "Bipolaris oryzae (Fungus)",
        "symptoms": "Oval or sesame seed-shaped dark brown spots with gray/white center on rice leaves.",
        "primary_conditions": "Nutritional stress (low potassium), humid cloudy canopy.",
        "management": "Mancozeb 75% WP @ 500 g/acre or Propiconazole 25% EC @ 200 ml/acre in 200 L water."
    },
    "Leaf Smut": {
        "causal_agent": "Entyloma oryzae (Fungus)",
        "symptoms": "Small, angular, leaden-black spots scattered on rice leaf blades.",
        "primary_conditions": "Humid canopy during grain filling.",
        "management": "Tricyclazole 75% WP @ 120 g/acre or Propiconazole @ 200 ml/acre."
    },
    "Diseased Leaf": {
        "causal_agent": "Xanthomonas citri pv. malvacearum / Foliar Complex",
        "symptoms": "Angular water-soaked leaf spots turning dark brown to black delimited by leaf veins on cotton.",
        "primary_conditions": "Warm, humid Kharif conditions (28-35°C).",
        "management": "Streptocycline @ 20 g + Copper Oxychloride 50% WP @ 500 g per acre in 200 L water."
    },
    "Red Rot": {
        "causal_agent": "Colletotrichum falcatum (Fungus)",
        "symptoms": "Yellowing and withering of 3rd/4th leaf from top on sugarcane; longitudinal split reveals reddened pith with crosswise white patches and alcoholic sour odor.",
        "primary_conditions": "Waterlogged fields, high humidity, warm monsoon weather.",
        "management": "Carbendazim sett treatment, Trichoderma harzianum soil application, rogue out infected clumps."
    },
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

