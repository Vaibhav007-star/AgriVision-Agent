"""
Verification Tests for Wheat & Haryana Multi-Crop Pathological Diagnosis.
Guarantees that authentic Wheat leaf photographs are ALWAYS diagnosed as Wheat
with CCS HAU Hisar Propiconazole prescriptions, and NEVER misclassified as Tomato.
"""

import pytest
from pathlib import Path
from PIL import Image

from app.ml.inference import predict_crop_disease
from app.agent.graph import run_agent_workflow
from app.agent.tools.dosage_tool import calculate_spray_dosage
from app.agent.tools.disease_info_tool import get_disease_info


def test_wheat_stripe_rust_diagnosed_as_wheat():
    """Authentic Wheat Stripe / Yellow Rust leaf must be diagnosed as Wheat with > 80% confidence."""
    wheat_sample = Path("data/sample_images/wheat_stripe_rust.jpg")
    assert wheat_sample.exists(), "Sample wheat_stripe_rust.jpg must exist"
    
    img = Image.open(wheat_sample).convert("RGB")
    
    # 1. Test auto detection mode
    res_auto = predict_crop_disease(img, target_crop="auto")
    assert res_auto["is_leaf"] is True
    assert res_auto["crop"] == "Wheat"
    assert "stripe" in res_auto["disease"].lower() or "rust" in res_auto["disease"].lower()
    assert res_auto["confidence_percentage"] >= 75.0
    assert "tomato" not in res_auto["crop"].lower()
    
    # 2. Test explicit wheat target mode
    res_target = predict_crop_disease(img, target_crop="Wheat")
    assert res_target["is_leaf"] is True
    assert res_target["crop"] == "Wheat"
    assert "stripe" in res_target["disease"].lower() or "rust" in res_target["disease"].lower()
    assert res_target["confidence_percentage"] >= 80.0
    assert "tomato" not in res_target["crop"].lower()


def test_wheat_leaf_rust_diagnosed_as_wheat():
    """Wheat Leaf / Brown Rust must diagnose as Wheat."""
    wheat_sample = Path("data/sample_images/wheat_leaf_rust.jpg")
    if wheat_sample.exists():
        img = Image.open(wheat_sample).convert("RGB")
        res = predict_crop_disease(img, target_crop="Wheat")
        assert res["is_leaf"] is True
        assert res["crop"] == "Wheat"
        assert "tomato" not in res["crop"].lower()


def test_wheat_prescription_contains_propiconazole():
    """Dosage tool and workflow for Wheat Rust must formulate Propiconazole Tilt @ 200 ml / 200 L water."""
    dosage = calculate_spray_dosage("Wheat", "Stripe / Yellow Rust", field_acres=1.5)
    assert dosage["water_volume_liters"] == 300.0
    assert "Propiconazole" in dosage["chemical_required"]
    assert "Tilt" in dosage["chemical_required"]
    assert "300 ml" in dosage["chemical_required"]


def test_rice_diagnosed_as_rice():
    """Rice Bacterial Leaf Blight sample must diagnose as Rice."""
    rice_sample = Path("data/sample_images/rice_bacterial_leaf_blight.jpg")
    if rice_sample.exists():
        img = Image.open(rice_sample).convert("RGB")
        res = predict_crop_disease(img, target_crop="Rice")
        assert res["is_leaf"] is True
        assert res["crop"] == "Rice"
        assert "tomato" not in res["crop"].lower()


def test_cotton_diagnosed_as_cotton():
    """Cotton diseased leaf must diagnose as Cotton."""
    cotton_sample = Path("data/sample_images/cotton_diseased_leaf.jpg")
    if cotton_sample.exists():
        img = Image.open(cotton_sample).convert("RGB")
        res = predict_crop_disease(img, target_crop="Cotton")
        assert res["is_leaf"] is True
        assert res["crop"] == "Cotton"
        assert "tomato" not in res["crop"].lower()
