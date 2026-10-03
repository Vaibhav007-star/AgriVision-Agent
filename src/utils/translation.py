"""
Bilingual Translation and Agricultural Localization Service for AgriVision Agent.
Provides seamless English <-> Hindi (हिंदी) agricultural vocabulary mapping,
contextual prompt translation, and farmer-friendly advisory generation.
"""

from typing import Dict, Any, Optional

# Agricultural Domain Translation Lexicon
AGRI_GLOSSARY_EN_TO_HI = {
    # Crops
    "Tomato": "टमाटर (Tomato)",
    "Potato": "आलू (Potato)",
    "Corn (Maize)": "मक्का (Corn)",
    "Corn": "मक्का (Corn)",
    "Apple": "सेब (Apple)",
    "Pepper Bell": "शिमला मिर्च (Bell Pepper)",
    "Pepper": "शिमला मिर्च (Bell Pepper)",
    
    # Diseases
    "Early Blight": "अगेती झुलसा रोग (Early Blight)",
    "Late Blight": "पछेती झुलसा रोग (Late Blight)",
    "Leaf Mold": "पत्ती फफूंद रोग (Leaf Mold)",
    "Common Rust": "सामान्य गेरुआ / रतुआ रोग (Common Rust)",
    "Northern Leaf Blight": "उत्तरी पत्ती झुलसा (Northern Leaf Blight)",
    "Apple Scab": "सेब का स्कैब रोग (Apple Scab)",
    "Black Rot": "काला सड़न रोग (Black Rot)",
    "Bacterial Spot": "जीवाणु धब्बा रोग (Bacterial Spot)",
    "Healthy": "स्वस्थ फसल (Healthy Crop)",
    
    # Agronomic Terms
    "Fungicide": "फफूंदनाशक",
    "Bactericide": "जीवाणुनाशक",
    "Biological Control": "जैविक एवं प्राकृतिक नियंत्रण",
    "Chemical Treatment": "रासायनिक उपचार एवं कीटनाशक",
    "Preventive Practices": "रोकथाम एवं बचाव के उपाय",
    "Water Volume": "पानी की मात्रा",
    "Knapsack Tanks": "नेप्सैक स्प्रे पंप (15 लीटर)",
    "High Risk": "उच्च जोखिम",
    "Moderate Risk": "मध्यम जोखिम",
    "Low Risk": "कम जोखिम",
    "Pre-Harvest Interval": "तुड़ाई से पूर्व प्रतीक्षा अवधि (PHI)"
}


def translate_crop_name(crop: str, target_lang: str = "hi") -> str:
    """Translates crop name to target language."""
    if target_lang != "hi":
        return crop
    return AGRI_GLOSSARY_EN_TO_HI.get(crop, crop)


def translate_disease_name(disease: str, target_lang: str = "hi") -> str:
    """Translates disease condition to target language."""
    if target_lang != "hi":
        return disease
    return AGRI_GLOSSARY_EN_TO_HI.get(disease, disease)


def generate_hindi_advisory(
    crop: str,
    disease: str,
    confidence: float,
    dosage_plan: Optional[Dict[str, Any]] = None,
    weather_risk: str = "Moderate"
) -> str:
    """
    Generates a natural, colloquial Hindi recommendation for farmers.
    """
    crop_hi = translate_crop_name(crop, "hi")
    disease_hi = translate_disease_name(disease, "hi")
    conf_pct = round(confidence * 100, 1) if confidence <= 1.0 else round(confidence, 1)
    
    if "healthy" in disease.lower():
        return (
            f"✅ **फसल स्थिति:** आपकी {crop_hi} की फसल पूरी तरह से **स्वस्थ** है (विश्वास स्तर: {conf_pct}%)।\n\n"
            f"🌱 **सुझाव:** किसी भी रासायनिक कीटनाशक के छिड़काव की आवश्यकता नहीं है। "
            f"नियमित सिंचाई करें और हर 25-30 दिन में नीम के तेल (3ml/लीटर) का छिड़काव करें ताकि फसल कीटों से सुरक्षित रहे।"
        )
        
    water_liters = dosage_plan.get("water_volume_liters", 200) if dosage_plan else 200
    tanks = dosage_plan.get("sprayer_tanks_15L", 13.3) if dosage_plan else 13.3
    chem_req = dosage_plan.get("chemical_required", "Mancozeb 75% WP") if dosage_plan else "Mancozeb 75% WP"
    
    risk_text = "अधिक नमी के कारण बीमारी फैलने का खतरा अधिक है" if "high" in weather_risk.lower() else "मौसम सामान्य है"
    
    return (
        f"⚠️ **रोग पहचान:** आपकी {crop_hi} की फसल में **{disease_hi}** के लक्षण पाए गए हैं (सटीकता: {conf_pct}%)।\n\n"
        f"🌦️ **मौसम चेतावनी:** {risk_text}।\n\n"
        f"🌿 **जैविक उपाय:**\n"
        f"- नीचे की रोगग्रस्त पत्तियों को काटकर खेत से दूर नष्ट कर दें।\n"
        f"- नीम का तेल (5 मिली प्रति लीटर पानी) में थोड़ा साबुन का घोल मिलाकर 7-10 दिन के अंतराल पर छिड़कें।\n\n"
        f"🧪 **रासायनिक उपचार एवं मात्रा (प्रति एकड़):**\n"
        f"- **दवा की मात्रा:** {chem_req}\n"
        f"- **घोल की मात्रा:** लगभग {water_liters} लीटर पानी (लगभग {tanks} स्प्रे पंप)।\n\n"
        f"🛡️ **सावधानी:** छिड़काव के समय मास्क और दस्ताने का प्रयोग करें। बारिश की संभावना होने पर छिड़काव न करें।"
    )

