"""
Diagnostic Scan History UI View (app/ui/history.py).
"""

import streamlit as st
import pandas as pd
from app.database.crud import get_recent_predictions


def render_history():
    """Renders database history of previous scans."""
    st.markdown("## 📜 Diagnostic Scan Audit History")
    st.caption("Auditable log of all recorded leaf diagnoses and prescriptions in SQLite.")
    
    scans = get_recent_predictions(limit=25)
    if scans:
        df = pd.DataFrame(scans)[["prediction_id", "timestamp", "crop", "disease", "confidence", "crop_stage", "language"]]
        df.columns = ["Scan ID", "Timestamp", "Crop", "Condition", "Confidence", "Growth Stage", "Lang"]
        st.dataframe(df, use_container_width=True)
        
        with st.expander("🔍 View Latest Recorded Prescription Detail", expanded=True):
            latest = scans[0]
            st.write(f"**Scan #{latest['prediction_id']} - {latest['crop']} ({latest['disease']})**")
            st.write(f"- **Confidence:** {float(latest['confidence'])*100:.1f}%")
            st.write(f"- **Crop Growth Stage:** {latest.get('crop_stage', 'Vegetative')}")
            st.write(f"- **AI Diagnosis / Recommendation:** {latest['recommendation']}")
            if latest.get('treatment'):
                st.write(f"- **Treatment:** {latest['treatment']}")
            if latest.get('prevention'):
                st.write(f"- **Prevention:** {latest['prevention']}")
    else:
        st.info("No recorded scans in database yet. Diagnostic runs from the Disease Detection page will be logged here.")

