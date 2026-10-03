"""
Bilingual Translation & Localization Service (app/services/translation.py).
Provides bidirectional English <-> Hindi (हिंदी) agricultural vocabulary mapping and advisory generation.
"""

from typing import Dict, Any, Optional
from src.utils.translation import (
    AGRI_GLOSSARY_EN_TO_HI,
    translate_crop_name,
    translate_disease_name,
    generate_hindi_advisory
)


def translate_text(text: str, target_lang: str = "hi") -> str:
    """Translates common agricultural terms to the target language."""
    if target_lang != "hi":
        return text
    return AGRI_GLOSSARY_EN_TO_HI.get(text, text)


def generate_bilingual_prescription(
    crop: str,
    disease: str,
    confidence: float,
    dosage_plan: Optional[Dict[str, Any]] = None,
    weather_risk: str = "Moderate",
    target_lang: str = "hi"
) -> str:
    """Generates localized advice in Hindi or English."""
    if target_lang == "hi":
        return generate_hindi_advisory(
            crop=crop,
            disease=disease,
            confidence=confidence,
            dosage_plan=dosage_plan,
            weather_risk=weather_risk
        )
    else:
        conf_pct = round(confidence * 100, 1) if confidence <= 1.0 else round(confidence, 1)
        chem = dosage_plan.get("chemical_required", "Mancozeb 75% WP") if dosage_plan else "Mancozeb 75% WP"
        return (
            f"🌾 **Crop Diagnosis:** {crop} — {disease} (Confidence: {conf_pct}%)\n\n"
            f"🌦️ **Weather Spore Risk:** {weather_risk}\n\n"
            f"🧪 **Recommended Chemical Treatment:** {chem}\n\n"
            f"🛡️ **Safety:** Wear protective gloves and avoid spraying before rainfall."
        )

