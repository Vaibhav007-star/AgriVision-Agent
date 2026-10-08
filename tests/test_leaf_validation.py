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
    # Synthetic skin patches with varied tone and realistic noise across Fitzpatrick I-VI
    tones = [
        [210, 160, 130],  # Fair / Asian tone
        [180, 130, 95],   # Olive / Medium tone
        [145, 95, 65],    # Deep / Dark tone
        [235, 185, 155],  # Light peach tone
        [195, 140, 105],  # Wheatish Indian tone
        [110, 65, 40]     # Deep dark tone
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


def test_face_with_green_background_is_strictly_rejected():
    """A human face standing in front of green plants, trees, or a green wall must still be rejected."""
    # 224x224 synthetic photo with green plant wall background + centered human face
    img = np.zeros((224, 224, 3), dtype=np.uint8)
    img[:, :] = [45, 125, 45] # Green plant background
    for y in range(40, 150):
        for x in range(60, 164):
            if ((x - 112) / 52) ** 2 + ((y - 95) / 55) ** 2 <= 1.0:
                img[y, x] = [185, 130, 95] # Human face
                
    face_img = Image.fromarray(img)
    res = validate_leaf_image(face_img)
    assert res["is_leaf"] is False, "Face with green background was erroneously accepted as leaf"
    assert res["reason"] == "human_or_skin_detected"


def test_face_with_green_clothing_is_strictly_rejected():
    """A human face wearing a green shirt or sweater must still be rejected."""
    img = np.zeros((224, 224, 3), dtype=np.uint8)
    img[:, :] = [225, 225, 230] # Neutral wall
    img[150:, :] = [35, 115, 45] # Green shirt
    for y in range(35, 145):
        for x in range(65, 160):
            if ((x - 112) / 47) ** 2 + ((y - 90) / 55) ** 2 <= 1.0:
                img[y, x] = [195, 140, 105] # Face
                
    face_img = Image.fromarray(img)
    res = validate_leaf_image(face_img)
    assert res["is_leaf"] is False, "Face with green clothing was erroneously accepted as leaf"
    assert res["reason"] == "human_or_skin_detected"


def test_selfie_portraits_are_strictly_rejected():
    """Close-up selfies and room portraits must be rejected regardless of lighting."""
    # Close-up selfie
    img = np.zeros((224, 224, 3), dtype=np.uint8)
    img[:, :] = [180, 180, 190]
    for y in range(20, 204):
        for x in range(30, 194):
            if ((x - 112) / 82) ** 2 + ((y - 112) / 92) ** 2 <= 1.0:
                img[y, x] = [175, 125, 85]
                
    selfie_img = Image.fromarray(img)
    res = validate_leaf_image(selfie_img)
    assert res["is_leaf"] is False
    assert res["reason"] == "human_or_skin_detected"



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


def test_predict_crop_disease_rejects_face_with_green_background():
    """predict_crop_disease must reject a face even if background contains green foliage."""
    img = np.zeros((224, 224, 3), dtype=np.uint8)
    img[:, :] = [45, 125, 45] # Green background
    for y in range(40, 150):
        for x in range(60, 164):
            if ((x - 112) / 52) ** 2 + ((y - 95) / 55) ** 2 <= 1.0:
                img[y, x] = [185, 130, 95] # Human face
                
    diag = predict_crop_disease(Image.fromarray(img))
    assert diag["is_leaf"] is False
    assert diag["confidence"] == 0.0
    assert diag["confidence_level"] == "Rejected"
    assert diag["disease"] == "No Plant Leaf Detected"
    assert diag["crop"] == "Non-Plant Object"
    assert len(diag["top_predictions"]) == 0
    assert "human" in diag["advisory_message"].lower() or "human" in diag["advisory_message_hi"]



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

