"""
Final Response & Formatting Node (app/agent/nodes/response.py).
Formats final natural language output in English and Hindi.
"""

from typing import Dict, Any
from app.agent.state import AgentState


def response_node(state: AgentState) -> Dict[str, Any]:
    """Formats final response and handles clarification if confidence was low."""
    steps = state.get("reasoning_steps", []).copy()
    clarification_needed = state.get("clarification_needed", False)
    lang = state.get("language", "en")
    rx = state.get("final_prescription", {})
    
    is_leaf = state.get("is_leaf", True)
    leaf_val = state.get("leaf_validation", {})
    
    if not is_leaf:
        if lang == "hi":
            final_text = leaf_val.get("message_hi", "⚠️ पत्ती की पहचान नहीं हुई: अपलोड की गई तस्वीर किसी पौधे की पत्ती नहीं है (मानव या गैर-पौधा वस्तु)। कृपया रोग निदान के लिए पौधे की पत्ती की स्पष्ट तस्वीर अपलोड करें।")
        else:
            final_text = leaf_val.get("message", "⚠️ Non-Leaf Image Detected: The uploaded image does not appear to be an agricultural crop leaf. AgriVision Agent is strictly designed for crop pathology (Tomato, Potato, Pepper, Apple, Corn). Please upload a clear photograph of an affected plant leaf to receive a diagnosis.")
        steps.append("🛑 [Response Node] Issued non-leaf input rejection advisory.")
    elif clarification_needed:
        if lang == "hi":
            final_text = "⚠️ रोग पहचान का विश्वास स्तर कम है। कृपया प्राकृतिक रोशनी में प्रभावित पत्ती की एक और स्पष्ट तस्वीर अपलोड करें।"
        else:
            final_text = "⚠️ Image confidence is below safe diagnostic threshold (60%). Please upload a clearer, well-lit photo showing the affected leaf area."
        steps.append("⚠️ [Response Node] Issued image clarification request to farmer.")
    else:
        if lang == "hi":
            final_text = rx.get("hindi_summary", "कृषि परामर्श तैयार कर दिया गया है।")
        else:
            final_text = (
                f"🌾 **AgriVision Agronomic Prescription:**\n\n"
                f"**Diagnosis:** {state.get('crop')} — {state.get('disease')} ({state.get('crop_stage', 'Vegetative')})\n\n"
                f"{rx.get('agent_explanation', '')}\n\n"
                f"**Key Chemical Recommendation:** {rx.get('chemical_controls', ['Contact local agronomist'])[0]}"
            )
        steps.append("🏁 [Response Node] Final multi-modal agronomic prescription ready.")
        
    return {
        "final_response": final_text,
        "reasoning_steps": steps
    }

