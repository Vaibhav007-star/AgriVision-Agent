"""
Deep Learning Inference and Grad-CAM Module for AgriVision Agent (app/ml/inference.py).
"""

from typing import Dict, Any, List, Optional, Union
from pathlib import Path
import json
import numpy as np
from PIL import Image
import tensorflow as tf

from app.ml.preprocessing import load_and_validate_image, preprocess_for_inference
from src.utils.image_processing import generate_gradcam_overlay

BASE_DIR = Path(__file__).resolve().parent.parent.parent


def predict_crop_disease(
    image_input: Union[str, Path, Image.Image, np.ndarray],
    model_path: Optional[str] = None,
    class_indices_path: Optional[str] = None,
    compute_gradcam: bool = True
) -> Dict[str, Any]:
    """
    Executes inference pipeline:
    Validate -> Resize (224x224) -> Normalize ([-1, 1]) -> Model Predict -> Top-3 -> Confidence Gate -> Grad-CAM.
    """
    if model_path is None:
        model_path = str(BASE_DIR / "models" / "saved_models" / "crop_disease_model.keras")
        if not Path(model_path).exists():
            model_path = str(BASE_DIR / "models" / "mobilenet_model.keras")
            
    if class_indices_path is None:
        class_indices_path = str(BASE_DIR / "models" / "saved_models" / "class_indices.json")
        if not Path(class_indices_path).exists():
            class_indices_path = str(BASE_DIR / "data" / "processed" / "class_indices.json")
            
    raw_img = load_and_validate_image(image_input)
    batch_tensor, resized_img = preprocess_for_inference(raw_img)
    
    # Load class indices
    class_indices = {}
    if Path(class_indices_path).exists():
        with open(class_indices_path, "r", encoding="utf-8") as f:
            raw_meta = json.load(f)
            class_indices = {int(k): v for k, v in raw_meta.items()}
            
    # Load model and predict
    model = None
    if Path(model_path).exists():
        model = tf.keras.models.load_model(model_path)
        preds = model.predict(batch_tensor, verbose=0)[0]
    else:
        num_c = len(class_indices) or 3
        preds = np.ones(num_c) / num_c
        
    top_k = min(3, len(preds))
    top_indices = np.argsort(preds)[::-1][:top_k]
    
    top_predictions = []
    for idx in top_indices:
        conf = float(preds[idx])
        meta = class_indices.get(idx, {
            "crop": "Tomato",
            "disease": f"Class {idx}",
            "is_healthy": False,
            "class_name": f"Class_{idx}"
        })
        top_predictions.append({
            "rank": len(top_predictions) + 1,
            "crop": meta.get("crop", "Tomato"),
            "disease": meta.get("disease", "Unknown"),
            "is_healthy": meta.get("is_healthy", False),
            "class_name": meta.get("class_name", f"Class_{idx}"),
            "confidence": round(conf, 4),
            "confidence_pct": f"{conf * 100:.1f}%"
        })
        
    best = top_predictions[0]
    best_conf = best["confidence"]
    
    # Confidence Level
    if best_conf >= 0.80:
        conf_level = "High"
        is_confident = True
        clarification_needed = False
        advice = "Diagnosis confidence is high. Treatment recommendations are ready."
    elif best_conf >= 0.60:
        conf_level = "Moderate"
        is_confident = True
        clarification_needed = False
        advice = "Diagnosis confidence is moderate. Cross-verification with visual symptoms is recommended."
    else:
        conf_level = "Low"
        is_confident = False
        clarification_needed = True
        advice = "Image confidence is low. Please upload a clearer image showing the affected leaf under natural lighting."
        
    # Grad-CAM
    cam_overlay = None
    if compute_gradcam and model is not None:
        try:
            last_conv = None
            for layer in reversed(model.layers):
                if isinstance(layer, (tf.keras.layers.Conv2D, tf.keras.layers.DepthwiseConv2D)):
                    last_conv = layer.name
                    break
            if last_conv:
                cam_overlay = generate_gradcam_overlay(model, raw_img, last_conv, top_indices[0])
        except Exception:
            cam_overlay = None
            
    return {
        "crop": best["crop"],
        "disease": best["disease"],
        "is_healthy": best["is_healthy"],
        "confidence": best_conf,
        "confidence_percentage": round(best_conf * 100, 1),
        "confidence_level": conf_level,
        "is_confident": is_confident,
        "clarification_needed": clarification_needed,
        "advisory_message": advice,
        "top_predictions": top_predictions,
        "gradcam_overlay": cam_overlay,
        "processed_image": resized_img
    }

