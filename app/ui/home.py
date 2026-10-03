"""
Home Overview Page View (app/ui/home.py).
"""

import streamlit as st
import pandas as pd


def render_home():
    """Renders the system overview and core capabilities."""
    st.markdown("## 🌿 Autonomous Plant Pathology & Agronomic Intelligence")
    st.markdown("""
    Welcome to **AgriVision Agent**, a state-of-the-art agricultural decision-support system. 
    Combining **Computer Vision**, **Transfer Learning CNNs (MobileNetV2)**, **Grad-CAM Attention Mapping**, 
    **FAISS Vector RAG**, and **LangGraph Autonomous State Machine**, AgriVision provides rapid, grounded, 
    and actionable crop disease diagnoses.
    """)
    
    # Feature Highlights Grid
    c1, c2, c3 = st.columns(3)
    with c1:
        st.markdown("""
        <div class="stat-box">
            <h4 style="margin:0; color:#1b5e20;">🔬 Deep Learning & CV</h4>
            <p style="font-size:0.88rem; color:#424242; margin-top:6px;">
                MobileNetV2 Transfer Learning with CLAHE enhancement, HSV segmentation, Top-3 probability ranking, and Grad-CAM visual heatmaps.
            </p>
        </div>
        """, unsafe_allow_html=True)
        
    with c2:
        st.markdown("""
        <div class="stat-box">
            <h4 style="margin:0; color:#1b5e20;">🤖 LangGraph Agent</h4>
            <p style="font-size:0.88rem; color:#424242; margin-top:6px;">
                Cyclic multi-node state graph orchestrating confidence gating (>60%), microclimate weather spore risks, and knapsack tank dosage calculations.
            </p>
        </div>
        """, unsafe_allow_html=True)
        
    with c3:
        st.markdown("""
        <div class="stat-box">
            <h4 style="margin:0; color:#1b5e20;">🌾 Grounded RAG</h4>
            <p style="font-size:0.88rem; color:#424242; margin-top:6px;">
                Dense vector search with FAISS over peer-reviewed pathology manuals, providing hallucination-free bilingual (EN/HI) guidance.
            </p>
        </div>
        """, unsafe_allow_html=True)
        
    st.markdown("<br>", unsafe_allow_html=True)
    
    # System Architecture Diagram
    st.markdown("### 🏗️ End-to-End System Architecture")
    st.code("""
  [Farmer Uploads Leaf Photo]
              │
              ▼
  [OpenCV Preprocessing & CLAHE]
              │
              ▼
  [MobileNetV2 Transfer Learning CNN]
              │
              ▼
  [Top-3 Classes & Confidence Gating]
              │
      ┌───────┴────────┐
      ▼                ▼
 [Conf >= 60%]    [Conf < 60%] ──► [Ask Farmer for Clearer Photo]
      │
      ▼
 ┌───────────────────────────────────────────────────┐
 │            LangGraph State Machine               │
 │                                                   │
 │  1. FAISS Vector Search (Pathology Documents)     │
 │  2. Weather Tool (Ambient RH & Spore Risk)        │
 │  3. Dosage Tool (Water Volume & Tank Calculations)│
 │  4. LLM Synthesis (Groq / Gemini / Local Ollama)  │
 └─────────────────────┬─────────────────────────────┘
                       │
                       ▼
 ┌───────────────────────────────────────────────────┐
 │             Streamlit Full-Stack UI               │
 │  - CNN Diagnosis & Top-3 Probabilities            │
 │  - Grad-CAM Lesion Attention Map                  │
 │  - Biological & Chemical Prescription Cards       │
 │  - English & Hindi Conversational Advisory        │
 │  - SQLite Scan Audit History & Telemetry          │
 └───────────────────────────────────────────────────┘
    """, language="text")

