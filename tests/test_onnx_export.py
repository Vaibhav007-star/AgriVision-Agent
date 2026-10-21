"""
Test Suite for ONNX In-Browser Edge AI Model (Pillar 6)
"""

import pytest
from pathlib import Path
import numpy as np
import onnxruntime as ort
import json


def test_onnx_model_file_exists():
    onnx_path = Path("app/static/models/agrivision_edge.onnx")
    assert onnx_path.exists()
    assert onnx_path.stat().st_size > 5_000_000  # > 5MB


def test_onnx_inference_execution():
    onnx_path = "app/static/models/agrivision_edge.onnx"
    session = ort.InferenceSession(onnx_path)
    
    input_name = session.get_inputs()[0].name
    output_name = session.get_outputs()[0].name
    
    assert input_name == "input_image"
    
    # Create normalized dummy leaf tensor (1, 224, 224, 3)
    dummy_input = np.random.uniform(0.0, 1.0, (1, 224, 224, 3)).astype(np.float32)
    outputs = session.run([output_name], {input_name: dummy_input})
    
    predictions = outputs[0]
    assert predictions.shape[0] == 1
    # Check softmax sum to approx 1.0
    assert np.isclose(np.sum(predictions), 1.0, atol=1e-3)


def test_class_names_json():
    classes_path = Path("app/static/models/class_names.json")
    assert classes_path.exists()
    with open(classes_path, "r", encoding="utf-8") as f:
        classes = json.load(f)
    assert len(classes) >= 3
    assert "Tomato___Early_blight" in classes
