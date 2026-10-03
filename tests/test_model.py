"""
Unit tests for Custom CNN, MobileNetV2 Transfer Learning, and Prediction Pipeline (tests/test_model.py).
"""

import unittest
from pathlib import Path
import numpy as np

from app.ml.model import build_custom_cnn, build_mobilenet_transfer_model
from app.ml.inference import predict_crop_disease


class TestModel(unittest.TestCase):
    
    def setUp(self):
        self.base_dir = Path(__file__).resolve().parent.parent
        self.sample_img_path = self.base_dir / "data" / "sample_images" / "tomato_early_blight.jpg"
        
    def test_custom_cnn_builder(self):
        model = build_custom_cnn(num_classes=3, input_shape=(224, 224, 3))
        self.assertIsNotNone(model)
        self.assertEqual(model.output_shape, (None, 3))
        self.assertIn("conv_block1_conv", [l.name for l in model.layers])
        
    def test_mobilenet_transfer_builder(self):
        model = build_mobilenet_transfer_model(num_classes=3, input_shape=(224, 224, 3), fine_tune_layers=0)
        self.assertIsNotNone(model)
        self.assertEqual(model.output_shape, (None, 3))
        
    def test_model_inference_pipeline(self):
        if self.sample_img_path.exists():
            res = predict_crop_disease(self.sample_img_path, compute_gradcam=False)
            self.assertIn("crop", res)
            self.assertIn("disease", res)
            self.assertIn("confidence", res)
            self.assertIn("top_predictions", res)
            self.assertGreaterEqual(len(res["top_predictions"]), 1)
            self.assertIn(res["confidence_level"], ["High", "Moderate", "Low"])


if __name__ == "__main__":
    unittest.main()

