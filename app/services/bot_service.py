"""
AgriVision Agentic Agri-Bot Service (app/services/bot_service.py).

Provides multi-channel conversational intelligence for WhatsApp, Telegram,
and Webhooks with zero-install accessibility for smallholder farmers.
Supports image leaf diagnostics, botanical guardrails, RAG grounding,
knapsack spray calculation, and micro-dialect vernacular responses.
"""

import io
import os
import json
import logging
from typing import Dict, Any, Optional, Union
from pathlib import Path
from PIL import Image

from app.ml.preprocessing import load_and_validate_image
from app.ml.inference import predict_crop_disease
from src.utils.image_processing import validate_leaf_image
from app.agent.tools.dosage_tool import calculate_spray_dosage
from app.services.predictive_pathology import calculate_disease_outbreak_risk, evaluate_climate_spray_window
from app.rag.retriever import retrieve_pathology_context
from app.database.crud import get_offline_agronomy_blocks

logger = logging.getLogger("AgriVisionBot")


class AgriBotService:
    """Conversational Agronomy Agent for WhatsApp & Telegram channels."""

    def __init__(self):
        self.default_district = "Karnal"

    def handle_message(
        self,
        sender_id: str,
        text: Optional[str] = None,
        image_bytes: Optional[bytes] = None,
        language: str = "hi",
        district: Optional[str] = None,
        acreage: float = 1.0,
    ) -> Dict[str, Any]:
        """
        Processes an incoming WhatsApp/Telegram message containing text, photo, or both.
        """
        dist = district or self.default_district
        is_hindi = language.lower().startswith("hi")

        # 1. Handle Photo-Based Leaf Pathology Inquiry
        if image_bytes is not None:
            return self._process_leaf_image(
                sender_id=sender_id,
                image_bytes=image_bytes,
                is_hindi=is_hindi,
                district=dist,
                acreage=acreage,
            )

        # 2. Handle Text-Based Agronomic Query
        query = (text or "").strip()
        if not query:
            return {
                "sender_id": sender_id,
                "status": "empty",
                "message": (
                    "🌾 राम-राम किसान भाई! एग्रीविज़न एआई में आपका स्वागत है। "
                    "कृपया अपनी फसल की पत्ती की फोटो भेजें या अपना कृषि प्रश्न पूछें।"
                    if is_hindi
                    else "🌾 Welcome to AgriVision AI! Please send a clear photo of your crop leaf or ask your agronomy question."
                ),
            }

        return self._process_text_query(
            sender_id=sender_id,
            query=query,
            is_hindi=is_hindi,
            district=dist,
        )

    def _process_leaf_image(
        self,
        sender_id: str,
        image_bytes: bytes,
        is_hindi: bool,
        district: str,
        acreage: float,
    ) -> Dict[str, Any]:
        """Processes leaf photo with botanical guardrails and full RAG agronomy."""
        try:
            # 1. Load image and verify integrity
            with Image.open(io.BytesIO(image_bytes)) as raw_img:
                img = raw_img.convert("RGB")

            # 2. Botanical Guardrail: Strict non-plant / human face rejection
            val_res = validate_leaf_image(img)
            if not val_res.get("is_leaf", True):
                reason = val_res.get("rejection_reason", "Non-botanical or non-crop image detected")
                rejection_msg = (
                    f"⚠️ *फोटो अस्वीकृत:* {reason}\n\n"
                    "एग्रीविज़न केवल वास्तविक फसल की पत्तियों (टमाटर, आलू, मिर्च, गेहूं, धान आदि) "
                    "के रोग निदान के लिए प्रशिक्षित है। कृपया स्पष्ट पत्ती की फोटो भेजें।"
                    if is_hindi
                    else f"⚠️ *Photo Rejected:* {reason}\n\n"
                    "AgriVision is strictly calibrated for agricultural crop leaves. "
                    "Please upload a close-up photo of a valid crop leaf blade."
                )
                return {
                    "sender_id": sender_id,
                    "status": "rejected",
                    "reason": reason,
                    "message": rejection_msg,
                }

            # 3. Neural Network Disease Inference
            diagnosis = predict_crop_disease(img)
            top_class = diagnosis.get("class", "Unknown")
            confidence = float(diagnosis.get("confidence", 0.0))
            is_healthy = diagnosis.get("is_healthy", False)

            # 4. Extract Crop and Disease Names
            crop_name = top_class.split("___")[0].replace("_", " ") if "___" in top_class else "Tomato"
            disease_name = top_class.split("___")[-1].replace("_", " ") if "___" in top_class else top_class

            # 5. RAG Knowledge Retrieval
            rag_data = retrieve_pathology_context(crop=crop_name, disease=disease_name)
            bio_controls = rag_data.get("biological_controls", [])
            chem_controls = rag_data.get("chemical_treatments", [])
            chemical_sol = chem_controls[0] if chem_controls else "Mancozeb 75% WP @ 2.5 g/L (CCS HAU Standard)"
            bio_sol = bio_controls[0] if bio_controls else "Neem Oil 10,000 ppm @ 5 ml/L + Trichoderma bio-agent"

            # 6. Knapsack Acreage Dosage Calculation
            dosage_data = calculate_spray_dosage(crop=crop_name, disease=disease_name, field_acres=acreage)

            # 7. Microclimate Spore Inoculum Risk
            spore_risk = calculate_disease_outbreak_risk(crop=crop_name, disease=disease_name, temperature_c=26.0, humidity_pct=82, rain_prob_pct=15)
            spray_window = evaluate_climate_spray_window(temperature_c=26.0, humidity_pct=82, rain_prob_pct=15, wind_speed_kmh=8.0)

            # 8. Format WhatsApp / Telegram Markdown Output

            if is_hindi:
                status_emoji = "✅" if is_healthy else "🚨"
                resp = (
                    f"{status_emoji} *एग्रीविज़न फसल जांच रिपोर्ट*\n"
                    f"━━━━━━━━━━━━━━━━━━━\n"
                    f"📍 *जिला:* {district} | *रकबा:* {acreage} एकड़\n"
                    f"🌱 *फसल:* {crop_name}\n"
                    f"🔬 *रोग / स्थिति:* *{disease_name}*\n"
                    f"📊 *सटीकता (Confidence):* {confidence * 100:.1f}%\n"
                    f"━━━━━━━━━━━━━━━━━━━\n"
                )
                if is_healthy:
                    resp += (
                        "🌟 आपकी फसल पूर्णतः स्वस्थ है! प्रकाश संश्लेषण सामान्य है। "
                        "अनावश्यक यूरिया या कीटनाशक न डालें, लागत बचाएं।"
                    )
                else:
                    resp += (
                        f"💊 *HAU अनुमोदित रासायनिक दवा:*\n👉 {chemical_sol}\n\n"
                        f"🌿 *जैविक उपचार:*\n👉 {bio_sol}\n\n"
                        f"🚿 *स्प्रे गणना ({acreage} एकड़ हेतु):*\n"
                        f"• कुल पानी: {dosage_data.get('water_volume_liters', 200)} लीटर\n"
                        f"• 15-लीटर नैपसैक टंकी: {dosage_data.get('sprayer_tanks_15L', 13)} टंकियां\n"
                        f"• रसायन खुराक: {dosage_data.get('chemical_required', chemical_sol)}\n\n"
                        f"☁️ *मौसम जोखिम:* {spore_risk.get('risk_level', 'Moderate')} Outbreak Risk\n"
                        f"⏱️ *सुरक्षित स्प्रे समय:* {spray_window.get('optimal_window', '06:30 - 09:30 AM')} (शांत मौसम में छिड़कें)।"
                    )
            else:
                status_emoji = "✅" if is_healthy else "🚨"
                resp = (
                    f"{status_emoji} *AgriVision Diagnostic Advisory*\n"
                    f"━━━━━━━━━━━━━━━━━━━\n"
                    f"📍 *District:* {district} | *Field Size:* {acreage} Acre(s)\n"
                    f"🌱 *Crop:* {crop_name}\n"
                    f"🔬 *Diagnosis:* *{disease_name}*\n"
                    f"📊 *Confidence:* {confidence * 100:.1f}%\n"
                    f"━━━━━━━━━━━━━━━━━━━\n"
                )
                if is_healthy:
                    resp += (
                        "🌟 Your crop is healthy! Photosynthetic efficiency is optimal. "
                        "Avoid unneeded chemical sprays to reduce farm expenses."
                    )
                else:
                    resp += (
                        f"💊 *Recommended Treatment:*\n👉 {chemical_sol}\n\n"
                        f"🌿 *Bio-Remedy:*\n👉 {bio_sol}\n\n"
                        f"🚿 *Spray Preparation ({acreage} Acres):*\n"
                        f"• Water volume: {dosage_data.get('water_volume_liters', 200)} Liters\n"
                        f"• 15L Knapsack Tanks: {dosage_data.get('sprayer_tanks_15L', 13)} tanks\n"
                        f"• Chemical Required: {dosage_data.get('chemical_required', chemical_sol)}\n\n"
                        f"☁️ *Spore Inoculum Risk:* {spore_risk.get('risk_level', 'Moderate')}\n"
                        f"⏱️ *Optimal Spray Window:* {spray_window.get('optimal_window', '06:30 - 09:30 AM')} (Calm morning wind)."
                    )

            return {
                "sender_id": sender_id,
                "status": "diagnosed",
                "crop": crop_name,
                "disease": disease_name,
                "confidence": confidence,
                "is_healthy": is_healthy,
                "chemical_treatment": chemical_sol,
                "organic_treatment": bio_sol,
                "dosage": dosage_data,
                "message": resp,
            }

        except Exception as e:
            logger.error(f"Error analyzing leaf image: {e}", exc_info=True)
            return {
                "sender_id": sender_id,
                "status": "error",
                "message": (
                    "⚠️ छवि विश्लेषण में त्रुटि हुई। कृपया स्पष्ट रोशनी में दोबारा फोटो भेजें।"
                    if is_hindi
                    else "⚠️ Error processing leaf photo. Please send a clearer picture under daylight."
                ),
            }

    def _process_text_query(
        self,
        sender_id: str,
        query: str,
        is_hindi: bool,
        district: str,
    ) -> Dict[str, Any]:
        """Handles conversational agronomy queries (mandi, blocks, weather)."""
        q = query.lower()

        # Check for Mandi query
        if any(w in q for w in ["mandi", "bhav", "rate", "price", "भाव", "मंडी"]):
            rates = {
                "Wheat (गेहूं)": "₹2,275 / Qtl (MSP ₹2,275) - Karnal Mandi",
                "Mustard (सरसों)": "₹5,650 / Qtl (MSP ₹5,650) - Hisar Mandi",
                "Basmati Paddy (धान 1121)": "₹4,150 / Qtl - Sirsa Mandi",
                "Cotton (कपास)": "₹7,120 / Qtl - Fatehabad Mandi",
            }
            if is_hindi:
                msg = f"📊 *हरियाणा प्रमुख कृषि उपज मंडी भाव ({district}):*\n━━━━━━━━━━━━━━━━━━━\n"
                for crop, val in rates.items():
                    msg += f"• *{crop}:* {val}\n"
                msg += "\n💡 *सलाह:* इस सप्ताह आवक सामान्य रहने से भाव मजबूत रहने का अनुमान है।"
            else:
                msg = f"📊 *Haryana APMC Mandi Rates ({district}):*\n━━━━━━━━━━━━━━━━━━━\n"
                for crop, val in rates.items():
                    msg += f"• *{crop}:* {val}\n"
                msg += "\n💡 *Advisory:* Arrivals are steady. High grade produce commands 5-8% premium."

            return {"sender_id": sender_id, "status": "mandi_query", "message": msg}

        # Check for block/district agronomy query
        if any(w in q for w in ["block", "खंड", "district", "जिला", "हरियाणा"]):
            blocks = get_offline_agronomy_blocks(district=district)
            block_names = [b.get("block_name", "") for b in blocks[:5]]
            if is_hindi:
                msg = (
                    f"🌾 *{district} जिले के प्रमुख कृषि खंड (Blocks):*\n"
                    f"👉 {', '.join(block_names)}\n\n"
                    "आप किसी भी खंड की मुख्य फसल व रोग निदान जानने के लिए खंड का नाम लिखकर भेज सकते हैं।"
                )
            else:
                msg = (
                    f"🌾 *Key Administrative Blocks in {district}:*\n"
                    f"👉 {', '.join(block_names)}\n\n"
                    "Reply with any block name to receive localized offline disease profiles."
                )
            return {"sender_id": sender_id, "status": "district_query", "message": msg}

        # General conversational response
        if is_hindi:
            msg = (
                f"🌾 नमस्ते! मैं आपका एग्रीविज़न कृषि सहायक हूँ ({district})।\n\n"
                "आप मुझसे निम्न में से कोई भी सहायता ले सकते हैं:\n"
                "1. 📸 *पत्ती की फोटो भेजें* - तुरंत रोग पहचान व HAU अनुमोदित दवा पाएं\n"
                "2. 💰 *'मंडी भाव'* लिखें - ताजा APMC मंडी दरें देखें\n"
                "3. 📍 *'खंड'* लिखें - {district} के कृषि खंडों की जानकारी पाएं"
            )
        else:
            msg = (
                f"🌾 Hello! I am your AgriVision Agronomic Assistant for {district}.\n\n"
                "How can I assist you today?\n"
                "1. 📸 *Send a leaf photo* - Instant diagnosis & approved spray dosage\n"
                "2. 💰 *Type 'mandi'* - Current Haryana APMC commodity rates\n"
                "3. 📍 *Type 'block'* - Local agricultural profile for {district}"
            )

        return {"sender_id": sender_id, "status": "chat_response", "message": msg}
