"""
Tests for Botanical Leaf & Out-of-Distribution (OOD) Guardrail.
Validates that genuine crop leaves are recognized while human subjects,
animals, and non-plant objects are strictly rejected with zero treatment formulation.
"""

import pytest
import numpy as np
from PIL import Image
from pathlib import Path

from src.utils.image_processing import validate_leaf_image
from app.ml.inference import predict_crop_disease
from app.agent.graph import run_agent_workflow


def test_benchmark_leaves_pass_validation():
    """All benchmark crop leaf photos must pass leaf validation."""
    sample_dir = Path("data/sample_images")
    sample_images = list(sample_dir.glob("*.jpg"))
    assert len(sample_images) > 0, "No sample images found to test"
    
    for s_path in sample_images:
        img = Image.open(s_path).convert("RGB")
        res = validate_leaf_image(img)
        assert res["is_leaf"] is True, f"Failed on valid crop leaf: {s_path.name} (Result: {res})"
        assert res["foliage_percentage"] >= 10.0, f"Foliage coverage too low on {s_path.name}"
        assert res["reason"] == "valid_leaf"


def test_human_skin_and_faces_are_rejected():
    """Human skin tones must be detected and rejected with reason 'human_or_skin_detected'."""
    # Synthetic skin patches with varied tone and realistic noise
    tones = [
        [210, 160, 130],  # Fair / Asian tone
        [180, 130, 95],   # Olive / Medium tone
        [145, 95, 65],    # Deep / Dark tone
        [235, 185, 155]   # Light peach tone
    ]
    np.random.seed(42)
    for tone in tones:
        base = np.full((224, 224, 3), tone, dtype=np.float32)
        noise = np.random.normal(0, 10, base.shape)
        skin_img = Image.fromarray(np.clip(base + noise, 0, 255).astype(np.uint8))
        
        res = validate_leaf_image(skin_img)
        assert res["is_leaf"] is False, f"Failed to reject human tone {tone}"
        assert res["reason"] == "human_or_skin_detected"
        assert "Human" in res["message"] or "human" in res["message"].lower()


def test_non_plant_objects_are_rejected():
    """Non-plant objects (blue clothing, red fruit/cars, blank surfaces) must be rejected."""
    # Blank surface (zero texture)
    blank_img = Image.fromarray(np.full((224, 224, 3), [240, 240, 240], dtype=np.uint8))
    res_blank = validate_leaf_image(blank_img)
    assert res_blank["is_leaf"] is False
    assert res_blank["reason"] == "blank_or_uniform_surface"

    # Blue object / vehicle / sky
    np.random.seed(10)
    blue_base = np.full((224, 224, 3), [40, 60, 210], dtype=np.float32)
    blue_noisy = np.clip(blue_base + np.random.normal(0, 12, blue_base.shape), 0, 255).astype(np.uint8)
    res_blue = validate_leaf_image(Image.fromarray(blue_noisy))
    assert res_blue["is_leaf"] is False
    assert res_blue["reason"] == "non_plant_object"

    # Red garment / surface
    red_base = np.full((224, 224, 3), [220, 30, 30], dtype=np.float32)
    red_noisy = np.clip(red_base + np.random.normal(0, 12, red_base.shape), 0, 255).astype(np.uint8)
    res_red = validate_leaf_image(Image.fromarray(red_noisy))
    assert res_red["is_leaf"] is False


def test_predict_crop_disease_rejects_human_input():
    """predict_crop_disease must short-circuit on non-leaf images with 0 confidence."""
    skin_patch = np.full((224, 224, 3), [210, 160, 130], dtype=np.float32)
    noise = np.random.normal(0, 10, skin_patch.shape)
    skin_img = Image.fromarray(np.clip(skin_patch + noise, 0, 255).astype(np.uint8))
    
    diag = predict_crop_disease(skin_img)
    assert diag["is_leaf"] is False
    assert diag["confidence"] == 0.0
    assert diag["confidence_level"] == "Rejected"
    assert diag["disease"] == "No Plant Leaf Detected"
    assert diag["crop"] == "Non-Plant Object"
    assert len(diag["top_predictions"]) == 0
    assert diag["gradcam_overlay"] is None


def test_agent_workflow_suppresses_treatment_for_non_leaf():
    """Agent workflow must never recommend fungicides or spray tanks for non-leaf input."""
    leaf_val = {
        "is_leaf": False,
        "reason": "human_or_skin_detected",
        "message": "Human detected. AgriVision is designed for plant leaf pathology.",
        "message_hi": "मानव चेहरा या त्वचा पहचानी गई है।"
    }
    
    agent_result = run_agent_workflow(
        crop="Non-Plant Object",
        disease="No Plant Leaf Detected",
        confidence=0.0,
        field_acres=2.0,
        is_leaf=False,
        leaf_validation=leaf_val
    )
    
    # Must have bypassed weather, RAG, and chemicals
    assert agent_result["is_confident"] is False
    assert agent_result["clarification_needed"] is True
    assert agent_result["confidence_level"] == "Rejected"
    assert len(agent_result["treatment"]) == 0
    assert "Human detected" in agent_result["final_response"] or "Non-Leaf" in agent_result["final_response"]

