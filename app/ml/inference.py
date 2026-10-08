"""
Deep Learning Inference and Grad-CAM Module for AgriVision Agent (app/ml/inference.py).
"""

from typing import Dict, Any, List, Optional, Union
from pathlib import Path
import json
import numpy as np
from PIL import Image
try:
    import tensorflow as tf
except Exception:
    tf = None

from app.ml.preprocessing import load_and_validate_image, preprocess_for_inference
from src.utils.image_processing import generate_gradcam_overlay, validate_leaf_image

BASE_DIR = Path(__file__).resolve().parent.parent.parent


def predict_crop_disease(
    image_input: Union[str, Path, Image.Image, np.ndarray],
    model_path: Optional[str] = None,
    class_indices_path: Optional[str] = None,
    compute_gradcam: bool = True,
    target_crop: str = "auto"
) -> Dict[str, Any]:
    """
    Executes inference pipeline:
    Leaf Validation -> Resize (224x224) -> Normalize ([-1, 1]) -> Model Predict -> Top-3 -> Confidence Gate -> Target Crop Consistency -> Grad-CAM.
    Only evaluates authentic project crops (Tomato, Potato, Pepper, Apple, Corn).
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
    
    # 0. Botanical & Out-of-Distribution Leaf Guardrail
    leaf_validation = validate_leaf_image(raw_img)
    if not leaf_validation["is_leaf"]:
        return {
            "is_leaf": False,
            "crop": "Non-Plant Object",
            "disease": "No Plant Leaf Detected",
            "is_healthy": False,
            "confidence": 0.0,
            "confidence_percentage": 0.0,
            "confidence_level": "Rejected",
            "is_confident": False,
            "clarification_needed": True,
            "advisory_message": leaf_validation["message"],
            "advisory_message_hi": leaf_validation.get("message_hi", "पौधे की पत्ती नहीं पाई गई।"),
            "top_predictions": [],
            "gradcam_overlay": None,
            "processed_image": resized_img,
            "leaf_validation": leaf_validation
        }
    
    # Load class indices
    class_indices = {}
    if Path(class_indices_path).exists():
        with open(class_indices_path, "r", encoding="utf-8") as f:
            raw_meta = json.load(f)
            class_indices = {int(k): v for k, v in raw_meta.items()}
            
    # Load model and predict
    model = None
    preds = None
    if tf is not None and Path(model_path).exists():
        try:
            model = tf.keras.models.load_model(model_path)
            preds = model.predict(batch_tensor, verbose=0)[0]
        except Exception:
            model = None
            preds = None

    if preds is None:
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
    
    # Target Crop Consistency Check:
    # If the user selected a specific project crop (e.g., "Tomato", "Potato"), verify image matches
    if target_crop and target_crop.lower() != "auto":
        norm_target = target_crop.strip().lower()
        pred_crop = best["crop"].strip().lower()
        # Check if predicted crop matches target
        crop_matches = (norm_target in pred_crop) or (pred_crop in norm_target)
        if not crop_matches:
            return {
                "is_leaf": False,
                "crop": f"Non-{target_crop} Subject",
                "disease": "Target Crop Mismatch",
                "is_healthy": False,
                "confidence": 0.0,
                "confidence_percentage": round(best_conf * 100, 1),
                "confidence_level": "Rejected",
                "is_confident": False,
                "clarification_needed": True,
                "advisory_message": f"Target crop mismatch: You specified '{target_crop}', but the image does not match {target_crop} foliage (predicted: '{best['crop']}'). AgriVision only tests the specific selected crop.",
                "advisory_message_hi": f"लक्षित फसल बेमेल: आपने '{target_crop}' चुना था, लेकिन पत्ती {target_crop} से मेल नहीं खाती।",
                "top_predictions": [],
                "gradcam_overlay": None,
                "processed_image": resized_img,
                "leaf_validation": leaf_validation
            }

    # Strict OOD Softmax Confidence Gate:
    # If confidence is below 70%, the image is Out-of-Distribution (animal, landscape, or non-project plant)
    if best_conf < 0.70:
        return {
            "is_leaf": False,
            "crop": "Non-Project / OOD Subject",
            "disease": "Uncertain (Out-of-Distribution)",
            "is_healthy": False,
            "confidence": 0.0,
            "confidence_percentage": round(best_conf * 100, 1),
            "confidence_level": "Rejected",
            "is_confident": False,
            "clarification_needed": True,
            "advisory_message": f"Image classification confidence ({best_conf*100:.1f}%) is too low or out-of-distribution. AgriVision is strictly trained on project crops (Tomato, Potato, Pepper, Apple, Corn). Please test only authentic project crop leaves.",
            "advisory_message_hi": "छवि वर्गीकरण की सटीकता कम है या यह समर्थित परियोजना फसलों से संबंधित नहीं है। कृपया केवल समर्थित फसलों की स्पष्ट पत्ती अपलोड करें।",
            "top_predictions": [],
            "gradcam_overlay": None,
            "processed_image": resized_img,
            "leaf_validation": leaf_validation
        }
    
    # Confidence Level for genuine in-distribution leaves
    if best_conf >= 0.85:
        conf_level = "High"
        is_confident = True
        clarification_needed = False
        advice = "Diagnosis confidence is high. Treatment recommendations are ready."
    else:
        conf_level = "Moderate"
        is_confident = True
        clarification_needed = False
        advice = "Diagnosis confidence is moderate. Cross-verification with visual symptoms is recommended."
        
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
        "is_leaf": True,
        "leaf_validation": leaf_validation,
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

