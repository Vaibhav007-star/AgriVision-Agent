"""
Disease Detection & Computer Vision UI View (app/ui/detection.py).
"""

import streamlit as st
import numpy as np
import pandas as pd
from PIL import Image
from pathlib import Path
import os

from app.ml.preprocessing import load_and_validate_image, apply_clahe
from app.ml.inference import predict_crop_disease
from app.database.crud import save_prediction
from src.utils.image_processing import segment_leaf_mask
from src.utils.dataset import get_available_samples


def render_detection():
    """Renders the interactive leaf upload, CV preprocessing, and Deep Learning diagnosis."""
    st.markdown("## 🔍 Leaf Pathology Diagnosis & Computer Vision")
    st.caption("Upload a leaf photo or pick a benchmark sample to run MobileNetV2 Transfer Learning and Grad-CAM.")
    
    col_input, col_display = st.columns([1, 1])
    
    with col_input:
        st.markdown("#### 1. Input Leaf Image")
        input_source = st.radio("Choose Input Mode:", ["📁 Benchmark Samples", "📤 Upload Custom Image"], horizontal=True)
        
        selected_image = None
        sample_name = None
        
        if input_source == "📁 Benchmark Samples":
            samples = get_available_samples()
            if samples:
                sample_name = st.selectbox("Select Sample Condition:", list(samples.keys()))
                sample_path = samples[sample_name]
                selected_image = load_and_validate_image(sample_path)
            else:
                st.warning("No benchmark samples found. Please upload an image.")
        else:
            uploaded_file = st.file_uploader("Upload Leaf Photo (JPG/PNG)", type=["jpg", "jpeg", "png"])
            if uploaded_file is not None:
                selected_image = Image.open(uploaded_file).convert("RGB")
                sample_name = uploaded_file.name
                
        # Optional crop stage selection
        crop_stage = st.selectbox(
            "Current Crop Growth Stage:",
            ["Seedling / Nursery", "Vegetative Growth", "Flowering Stage", "Fruiting / Pod Formation", "Pre-Harvest"],
            index=1
        )
        
        if selected_image is not None:
            st.image(selected_image, caption="Original Input Leaf", use_container_width=True)
            
            # Interactive Computer Vision Preprocessing
            st.markdown("#### 2. Computer Vision Feature Extraction")
            cv_expander = st.expander("🛠️ View OpenCV Preprocessing & Foliage Mask", expanded=False)
            with cv_expander:
                c_cv1, c_cv2 = st.columns(2)
                with c_cv1:
                    enhanced_clahe = apply_clahe(selected_image)
                    st.image(enhanced_clahe, caption="CLAHE Contrast Enhanced", use_container_width=True)
                with c_cv2:
                    seg = segment_leaf_mask(selected_image)
                    st.image(seg["segmented_image"], caption=f"Foliage Mask (Lesion: {seg['lesion_percentage']}%)", use_container_width=True)
                    
            btn_run = st.button("🚀 Run Deep Learning Diagnostic Engine", type="primary", use_container_width=True)
        else:
            btn_run = False
            
    with col_display:
        st.markdown("#### 3. Deep Learning Diagnostic Output")
        
        if btn_run and selected_image is not None:
            with st.spinner("Executing MobileNetV2 Inference and Grad-CAM Backpropagation..."):
                result = predict_crop_disease(selected_image, compute_gradcam=True)
                st.session_state["latest_prediction"] = result
                st.session_state["latest_crop_stage"] = crop_stage
                
                # Save to database
                save_prediction(
                    crop=result["crop"],
                    disease=result["disease"],
                    confidence=result["confidence"],
                    crop_stage=crop_stage,
                    language=st.session_state.get("language", "en"),
                    recommendation=result["advisory_message"],
                    top3_predictions=result["top_predictions"]
                )
                
        if "latest_prediction" in st.session_state:
            pred = st.session_state["latest_prediction"]
            is_leaf = pred.get("is_leaf", True)
            
            if not is_leaf or pred.get("confidence_level") == "Rejected":
                st.error(f"🚫 **Input Rejected:** {pred.get('advisory_message', 'No valid crop leaf detected.')}")
                if st.session_state.get("language") == "hi" and pred.get("advisory_message_hi"):
                    st.caption(pred["advisory_message_hi"])
                st.warning("🛡️ **Botanical Guardrail Active:** This photo was identified as a human subject or non-plant object. AgriVision strictly suppresses disease prediction and chemical dosage to prevent hazardous misapplications.")
                st.info("📸 Please upload a clear close-up photograph of an affected crop leaf (Tomato, Potato, Pepper, Apple, Corn) in natural lighting.")
            else:
                # Confidence Banner
                if pred["confidence_level"] == "High":
                    st.markdown(f"""
                    <div class="result-card-healthy" style="border-left: 5px solid #2e7d32; padding: 12px; background: #e8f5e9; border-radius: 6px;">
                        <h3 style="margin:0; color:#1b5e20;">🌾 {pred['crop']} — {pred['disease']}</h3>
                        <p style="margin:4px 0 0 0; color:#2e7d32; font-weight:600;">
                            Confidence: {pred['confidence_percentage']}% ({pred['confidence_level']} Certainty) | Status: {'Healthy' if pred['is_healthy'] else 'Pathogen Detected'}
                        </p>
                    </div>
                    """, unsafe_allow_html=True)
                elif pred["confidence_level"] == "Moderate":
                    st.warning(f"🌾 **{pred['crop']} — {pred['disease']}** (Confidence: `{pred['confidence_percentage']}%` - Moderate Certainty)")
                else:
                    st.error(f"⚠️ **Low Confidence:** {pred['advisory_message']}")
                    
                # Grad-CAM Attention Map
                if pred.get("gradcam_overlay") is not None:
                    st.markdown("#### 🧠 Grad-CAM Neural Attention Map")
                    st.caption("Visualizing gradient activations on the final convolutional layer highlighting lesion hot-spots.")
                    st.image(pred["gradcam_overlay"], use_container_width=True)
                    
                # Top-3 Probability Distribution Table
                if pred.get("top_predictions"):
                    st.markdown("#### 📊 Top-3 Categorical Probability Distribution")
                    top_df = pd.DataFrame(pred["top_predictions"])[["rank", "crop", "disease", "confidence_pct"]]
                    top_df.columns = ["Rank", "Crop", "Condition", "Probability"]
                    st.dataframe(top_df, use_container_width=True)
                
                st.info("👉 Switch to the **🤖 AI Agent Diagnosis** page to review autonomous multi-node reasoning, acreage dosage, and RAG treatment plans.")
        else:
            st.info("👈 Select a sample or upload a leaf photo to trigger neural inference.")

