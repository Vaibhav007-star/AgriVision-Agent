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
    
    if clarification_needed:
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

