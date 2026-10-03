"""
Recommendation & Dosage Node (app/agent/nodes/recommendation.py).
Computes exact tank mixtures based on field acres and synthesizes biological/chemical plans.
"""

from typing import Dict, Any
from app.agent.state import AgentState
from app.agent.tools.dosage_tool import calculate_spray_dosage
from app.rag.retriever import retrieve_pathology_context
from src.utils.translation import generate_hindi_advisory


def recommendation_node(state: AgentState) -> Dict[str, Any]:
    """Calculates field dosage and synthesizes multi-factor treatment prescriptions."""
    steps = state.get("reasoning_steps", []).copy()
    crop = state.get("crop", "Tomato")
    disease = state.get("disease", "Early Blight")
    conf = state.get("confidence", 0.94)
    acres = state.get("field_acres", 1.0)
    stage = state.get("crop_stage", "Vegetative Growth")
    weather = state.get("weather", {})
    spore_risk = weather.get("spore_germination_risk", "Moderate")
    
    # Calculate acreage spray dosage
    dosage_plan = calculate_spray_dosage(crop, disease, field_acres=acres)
    
    # Retrieve RAG pathology
    rag_data = retrieve_pathology_context(crop, disease)
    
    # Generate bilingual summary
    hindi_adv = generate_hindi_advisory(crop, disease, conf, dosage_plan=dosage_plan, weather_risk=spore_risk)
    
    final_prescription = {
        "crop": crop,
        "disease": disease,
        "crop_stage": stage,
        "biological_controls": rag_data.get("biological_controls", []),
        "chemical_controls": rag_data.get("chemical_controls", []),
        "cultural_prevention": rag_data.get("cultural_prevention", []),
        "field_dosage": dosage_plan,
        "hindi_summary": hindi_adv,
        "sources": rag_data.get("sources", []),
        "agent_explanation": (
            f"Based on the visual diagnosis of {crop} {disease} during the {stage} stage, "
            f"and current microclimate conditions ({spore_risk} fungal inoculum pressure in {state.get('location', 'the region')}), "
            f"we formulated a calibrated tank mixture of {dosage_plan.get('water_volume_liters', 200)} Liters "
            f"({dosage_plan.get('sprayer_tanks_15L', 13.3)} knapsack tanks) for {acres} acre(s)."
        )
    }
    
    steps.append(f"🚜 [Recommendation Node] Formulated treatment plan for {acres} acre(s): {dosage_plan.get('water_volume_liters', 200)}L water / {dosage_plan.get('sprayer_tanks_15L', 13.3)} tanks.")
    
    return {
        "dosage_plan": dosage_plan,
        "treatment": rag_data.get("chemical_controls", []),
        "prevention": rag_data.get("cultural_prevention", []),
        "final_prescription": final_prescription,
        "reasoning_steps": steps
    }

