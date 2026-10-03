"""
AI Agent Diagnosis & Prescriptions UI View (app/ui/agent.py).
"""

import streamlit as st
import pandas as pd
from app.agent.graph import run_agent_workflow
from src.config import config


def render_agent():
    """Renders the autonomous AI Agent reasoning, knapsack dosage, and RAG prescriptions."""
    st.markdown("## 🤖 Autonomous Agentic AI Reasoning & Prescription")
    st.caption("Multi-node LangGraph state machine orchestrating Computer Vision, FAISS RAG, Weather tools, and Dosage calculations.")
    
    pred = st.session_state.get("latest_prediction", None)
    active_crop = pred["crop"] if pred else "Tomato"
    active_disease = pred["disease"] if pred else "Early Blight"
    active_conf = pred["confidence"] if pred else 0.948
    active_stage = st.session_state.get("latest_crop_stage", "Vegetative Growth")
    
    # Field Parameters
    c_p1, c_p2, c_p3 = st.columns([1, 1, 1])
    with c_p1:
        target_crop = st.selectbox("Target Crop", ["Tomato", "Potato", "Corn (Maize)", "Apple", "Pepper Bell"], index=0 if "Tomato" in active_crop else 1)
    with c_p2:
        target_disease = st.selectbox("Target Condition", ["Early Blight", "Late Blight", "Common Rust", "Bacterial Spot", "Healthy"], index=0 if "Early" in active_disease else 1)
    with c_p3:
        field_acres = st.number_input("Field Area (Acres)", min_value=0.25, max_value=50.0, value=1.5, step=0.5)
        
    lang = st.session_state.get("language", "en")
    
    # Run Agent Workflow
    with st.spinner("Executing LangGraph State-Based Agent Workflow..."):
        agent_result = run_agent_workflow(
            crop=target_crop,
            disease=target_disease,
            confidence=active_conf,
            field_acres=field_acres,
            location=config.services.DEFAULT_LOCATION,
            language=lang
        )
        
    prescription = agent_result.get("final_prescription", {})
    weather = agent_result.get("weather_data", {})
    dosage = agent_result.get("dosage_plan", {})
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.markdown("### 🧭 Live Agent State Execution Graph")
        for step in agent_result.get("reasoning_steps", []):
            st.markdown(f"""
            <div class="step-card" style="background:#f1f8e9; border-left:4px solid #33691e; padding:8px 12px; margin-bottom:8px; border-radius:4px;">
                <span style="color:#1b5e20; font-weight:600;">{step}</span>
            </div>
            """, unsafe_allow_html=True)
            
        st.markdown("#### 🚜 Field Spray & Tank Dosage Plan")
        if dosage:
            d_col1, d_col2 = st.columns(2)
            d_col1.metric("Total Water Required", f"{dosage.get('water_volume_liters', 200)} Liters")
            d_col2.metric("Knapsack Tanks (15L)", f"{dosage.get('sprayer_tanks_15L', 13.3)} Tanks")
            st.write(f"- **Chemical Quantity:** `{dosage.get('chemical_required', 'N/A')}`")
            st.write(f"- **Organic Quantity:** `{dosage.get('organic_required', 'N/A')}`")
            st.write(f"- **Required PPE:** {', '.join(dosage.get('safety_equipment', []))}")
            st.write(f"- **Current Crop Stage:** `{active_stage}`")
            
        if weather:
            st.markdown("#### 🌦️ Microclimate Environmental Gate")
            st.info(f"**Location:** {weather.get('location', '')} | **Spore Germination Risk:** `{weather.get('spore_germination_risk', 'Moderate')}` (RH: {weather.get('humidity_pct', 80)}%)\n\n*{weather.get('agronomic_advice', '')}*")
            
    with col2:
        st.markdown("### 📋 Formulated Agronomic Action Plan")
        
        # Bilingual summary banner
        if lang == "hi" or "hindi_summary" in prescription:
            st.success(f"🌾 **हिंदी में सलाह (Hindi Summary):**\n\n{prescription.get('hindi_summary', '')}")
            
        if prescription.get("agent_explanation"):
            with st.expander("🤖 AI Agronomist Reasoning & Synthesis", expanded=True):
                st.write(prescription["agent_explanation"])
                
        with st.expander("🌱 Organic / Biological Control", expanded=True):
            for bio in prescription.get("biological_controls", []):
                st.write(f"- {bio}")
                
        with st.expander("🧪 Chemical / Fungicide Treatment", expanded=True):
            for chem in prescription.get("chemical_controls", []):
                st.write(f"- {chem}")
                
        with st.expander("🛡️ Preventive Practices for Next Cycle", expanded=True):
            for cult in prescription.get("cultural_prevention", []):
                st.write(f"- {cult}")

