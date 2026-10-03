"""
Robust Image Inference & Prediction Engine for AgriVision Agent.
Implements: Load -> Validate -> Resize -> Normalize -> Prediction -> Top-3 -> Confidence Gating.
"""

from typing import Dict, Any, List, Tuple, Union, Optional
import os
import sys
from pathlib import Path
import json
import yaml
import numpy as np
from PIL import Image
import tensorflow as tf

# Ensure project root is in sys.path
BASE_DIR = Path(__file__).resolve().parent.parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from src.utils.image_processing import load_and_validate_image, generate_gradcam_overlay


class AgriVisionPredictor:
    """Production Inference Classifier with Confidence Thresholding & Explainability."""
    
    def __init__(self, model_path: Optional[str] = None, class_indices_path: Optional[str] = None):
        if model_path is None:
            model_path = str(BASE_DIR / "models" / "saved_models" / "crop_disease_model.keras")
            if not os.path.exists(model_path):
                model_path = str(BASE_DIR / "models" / "mobilenet_model.keras")
                
        if class_indices_path is None:
            class_indices_path = str(BASE_DIR / "models" / "saved_models" / "class_indices.json")
            if not os.path.exists(class_indices_path):
                class_indices_path = str(BASE_DIR / "data" / "processed" / "class_indices.json")
                
        self.model_path = model_path
        self.class_indices_path = class_indices_path
        self.model = None
        self.class_indices = {}
        self._load_resources()
        
    def _load_resources(self):
        """Loads serialized model and class index metadata."""
        if os.path.exists(self.model_path):
            self.model = tf.keras.models.load_model(self.model_path)
            
        if os.path.exists(self.class_indices_path):
            with open(self.class_indices_path, "r", encoding="utf-8") as f:
                raw_indices = json.load(f)
                self.class_indices = {int(k): v for k, v in raw_indices.items()}
                
    def predict(
        self,
        image_input: Union[str, Path, Image.Image, np.ndarray],
        compute_gradcam: bool = True,
        compute_cam: Optional[bool] = None
    ) -> Dict[str, Any]:
        """
        Executes robust image inference pipeline.
        """
        if compute_cam is not None:
            compute_gradcam = compute_cam
        # 1. Load & Validate Image
        if isinstance(image_input, (str, Path)):
            raw_img = load_and_validate_image(image_input)
        elif isinstance(image_input, Image.Image):
            raw_img = image_input.convert("RGB")
        elif isinstance(image_input, np.ndarray):
            raw_img = Image.fromarray(image_input.astype("uint8")).convert("RGB")
        else:
            raise ValueError(f"Unsupported image input type: {type(image_input)}")
            
        # 2. Resize & Normalize (224x224, [-1, 1])
        img_resized = raw_img.resize((224, 224), Image.Resampling.LANCZOS)
        img_array = np.array(img_resized, dtype=np.float32)
        norm_tensor = (img_array / 127.5) - 1.0
        batch_tensor = np.expand_dims(norm_tensor, axis=0)
        
        # 3. Model Prediction
        if self.model is not None:
            preds = self.model.predict(batch_tensor, verbose=0)[0]
        else:
            # Fallback uniform distribution
            num_c = len(self.class_indices) or 3
            preds = np.ones(num_c) / num_c
            
        # 4. Extract Top-3 Predictions
        top_k = min(3, len(preds))
        top_indices = np.argsort(preds)[::-1][:top_k]
        
        top_predictions = []
        for idx in top_indices:
            conf = float(preds[idx])
            meta = self.class_indices.get(idx, {
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
            
        best_pred = top_predictions[0]
        best_conf = best_pred["confidence"]
        
        # 5. Confidence Thresholding
        if best_conf >= 0.80:
            confidence_level = "High"
            is_confident = True
            clarification_needed = False
            advice_msg = "Diagnosis confidence is high. Proceeding with formulated agronomic treatment."
        elif best_conf >= 0.60:
            confidence_level = "Moderate"
            is_confident = True
            clarification_needed = False
            advice_msg = "Diagnosis confidence is moderate. Recommended to cross-verify visual symptoms."
        else:
            confidence_level = "Low"
            is_confident = False
            clarification_needed = True
            advice_msg = "Image confidence is low. Please upload a clearer image showing the affected leaf under natural lighting."
            
        # 6. Optional Grad-CAM Heatmap
        cam_overlay = None
        if compute_gradcam and self.model is not None:
            try:
                # Find last Conv2D layer
                last_conv = None
                for layer in reversed(self.model.layers):
                    if isinstance(layer, (tf.keras.layers.Conv2D, tf.keras.layers.DepthwiseConv2D)):
                        last_conv = layer.name
                        break
                if last_conv:
                    cam_overlay = generate_gradcam_overlay(self.model, raw_img, last_conv, top_indices[0])
            except Exception:
                cam_overlay = None
                
        return {
            "crop": best_pred["crop"],
            "disease": best_pred["disease"],
            "is_healthy": best_pred["is_healthy"],
            "confidence": best_conf,
            "confidence_percentage": round(best_conf * 100, 1),
            "confidence_level": confidence_level,
            "is_confident": is_confident,
            "clarification_needed": clarification_needed,
            "advisory_message": advice_msg,
            "top_predictions": top_predictions,
            "gradcam_overlay": cam_overlay,
            "processed_image": img_resized
        }


# Singleton Predictor Instance
_PREDICTOR_INSTANCE: Optional[AgriVisionPredictor] = None

def predict_disease(image_input: Union[str, Path, Image.Image, np.ndarray], compute_cam: bool = True) -> Dict[str, Any]:
    """Global prediction entry point."""
    global _PREDICTOR_INSTANCE
    if _PREDICTOR_INSTANCE is None:
        _PREDICTOR_INSTANCE = AgriVisionPredictor()
    return _PREDICTOR_INSTANCE.predict(image_input, compute_gradcam=compute_cam)


if __name__ == "__main__":
    test_img = BASE_DIR / "data" / "sample_images" / "tomato_early_blight.jpg"
    if test_img.exists():
        res = predict_disease(test_img)
        print(f"Crop: {res['crop']} | Disease: {res['disease']} | Confidence: {res['confidence_percentage']}% ({res['confidence_level']})")

