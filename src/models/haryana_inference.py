"""
Haryana Multi-Crop GPU Inference Engine (src/models/haryana_inference.py).

Provides instant inference across all 33 disease classes of Haryana crops
using the trained MobileNetV2 PyTorch GPU model (or CPU fallback).
"""

import json
from pathlib import Path
from typing import Dict, Any, List, Optional, Tuple
from PIL import Image

import torch
import torch.nn as nn
from torchvision import transforms, models
from torchvision.models import mobilenet_v2

BASE_DIR = Path("c:/Projects/AgriVision Agent")
MODEL_PATH = BASE_DIR / "models" / "haryana_models" / "haryana_master_multicrop_gpu.pt"
CLASS_MAP_PATH = BASE_DIR / "models" / "haryana_models" / "haryana_class_map.json"

_DEVICE = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")
_MODEL: Optional[nn.Module] = None
_CLASS_NAMES: List[str] = []

_INFERENCE_TRANSFORM = transforms.Compose([
    transforms.Resize((224, 224)),
    transforms.ToTensor(),
    transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
])


def load_haryana_model():
    """Loads the 33-class Haryana master model into GPU or CPU memory."""
    global _MODEL, _CLASS_NAMES
    if _MODEL is not None:
        return _MODEL, _CLASS_NAMES
        
    if not MODEL_PATH.exists() or not CLASS_MAP_PATH.exists():
        raise FileNotFoundError(f"Haryana model or class map not found at {MODEL_PATH}")
        
    with open(CLASS_MAP_PATH, "r") as f:
        class_map = json.load(f)
        _CLASS_NAMES = [class_map[str(i)] for i in range(len(class_map))]
        
    num_classes = len(_CLASS_NAMES)
    model = mobilenet_v2()
    in_features = model.classifier[1].in_features
    model.classifier = nn.Sequential(
        nn.Dropout(p=0.3),
        nn.Linear(in_features, 512),
        nn.ReLU(),
        nn.Dropout(p=0.2),
        nn.Linear(512, num_classes)
    )
    
    checkpoint = torch.load(MODEL_PATH, map_location=_DEVICE)
    model.load_state_dict(checkpoint["model_state_dict"])
    model.to(_DEVICE)
    model.eval()
    _MODEL = model
    return _MODEL, _CLASS_NAMES


def parse_label(raw_class: str) -> Tuple[str, str]:
    """Parses raw class names into human-readable Crop and Disease."""
    if "___" in raw_class:
        parts = raw_class.split("___")
        crop = parts[0].replace("_", " ").title()
        disease = parts[1].replace("_", " ").title()
    elif "_" in raw_class:
        parts = raw_class.split("_", 1)
        crop = parts[0].title()
        disease = parts[1].replace("_", " ").title()
    else:
        crop = "Unknown"
        disease = raw_class
    return crop, disease


def predict_haryana_crop(image: Image.Image, top_k: int = 3) -> Dict[str, Any]:
    """
    Executes deep learning inference on an input leaf image across all Haryana crops.
    """
    model, class_names = load_haryana_model()
    
    # Preprocess
    img_rgb = image.convert("RGB")
    tensor = _INFERENCE_TRANSFORM(img_rgb).unsqueeze(0).to(_DEVICE)
    
    with torch.no_grad():
        logits = model(tensor)
        probs = torch.softmax(logits, dim=1).squeeze(0)
        
    top_probs, top_indices = torch.topk(probs, k=min(top_k, len(class_names)))
    
    top_predictions = []
    for rank, (prob, idx) in enumerate(zip(top_probs, top_indices), start=1):
        raw_name = class_names[idx.item()]
        crop, disease = parse_label(raw_name)
        top_predictions.append({
            "rank": rank,
            "raw_class": raw_name,
            "crop": crop,
            "disease": disease,
            "confidence": round(prob.item(), 4),
            "confidence_pct": f"{prob.item() * 100:.2f}%"
        })
        
    top_pred = top_predictions[0]
    return {
        "crop": top_pred["crop"],
        "disease": top_pred["disease"],
        "confidence": top_pred["confidence"],
        "confidence_percentage": top_pred["confidence_pct"],
        "is_healthy": "healthy" in top_pred["disease"].lower(),
        "top_predictions": top_predictions,
        "device_used": str(_DEVICE)
    }
