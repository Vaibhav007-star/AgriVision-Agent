"""
Diagnosis & Confidence Check Node (app/agent/nodes/diagnosis.py).
Validates whether the CNN detection exceeds the 60% confidence threshold.
"""

from typing import Dict, Any
from app.agent.state import AgentState
from app.agent.tools.crop_info_tool import get_crop_info
from app.agent.tools.disease_info_tool import get_disease_info


def diagnosis_node(state: AgentState) -> Dict[str, Any]:
    """Validates prediction confidence and enriches with botanical domain metadata."""
    steps = state.get("reasoning_steps", []).copy()
    conf = state.get("confidence", 0.94)
    crop = state.get("crop", "Tomato")
    disease = state.get("disease", "Early Blight")
    
    threshold = 0.60
    is_confident = conf >= threshold
    
    if is_confident:
        conf_level = "High" if conf >= 0.80 else "Moderate"
        steps.append(f"✅ [Diagnosis Node] Confidence check passed: {conf*100:.1f}% >= {threshold*100:.0f}% threshold ({conf_level} certainty).")
        clarification_needed = False
    else:
        conf_level = "Low"
        steps.append(f"⚠️ [Diagnosis Node] Low confidence: {conf*100:.1f}% < {threshold*100:.0f}%. Flagging clarification needed.")
        clarification_needed = True
        
    crop_info = get_crop_info(crop)
    disease_info = get_disease_info(crop, disease)
    
    return {
        "confidence_level": conf_level,
        "is_confident": is_confident,
        "clarification_needed": clarification_needed,
        "crop_info": crop_info,
        "disease_info": disease_info,
        "reasoning_steps": steps
    }

