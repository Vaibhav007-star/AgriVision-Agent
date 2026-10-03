"""
Unit and Integration tests for ML Architectures, Training & Prediction Pipeline (Phase 3).
"""

import unittest
from pathlib import Path
import numpy as np
import tensorflow as tf

from ml.models.custom_cnn import build_custom_cnn
from ml.models.mobilenet_model import build_mobilenetv2_model
from ml.inference.predict import AgriVisionPredictor, predict_disease


class TestMLPipeline(unittest.TestCase):
    
    def setUp(self):
        self.base_dir = Path(__file__).resolve().parent.parent
        self.sample_img = self.base_dir / "data" / "sample_images" / "tomato_early_blight.jpg"
        
    def test_custom_cnn_builder(self):
        model = build_custom_cnn(num_classes=3, input_shape=(224, 224, 3))
        self.assertIsInstance(model, tf.keras.Model)
        self.assertEqual(model.output_shape, (None, 3))
        
        # Dummy batch forward pass
        dummy_tensor = np.zeros((1, 224, 224, 3), dtype=np.float32)
        preds = model(dummy_tensor, training=False)
        self.assertEqual(preds.shape, (1, 3))
        self.assertAlmostEqual(float(np.sum(preds.numpy())), 1.0, places=4)
        
    def test_mobilenet_model_builder(self):
        model = build_mobilenetv2_model(num_classes=3, input_shape=(224, 224, 3), fine_tune_layers=0)
        self.assertIsInstance(model, tf.keras.Model)
        self.assertEqual(model.output_shape, (None, 3))
        
        dummy_tensor = np.zeros((1, 224, 224, 3), dtype=np.float32)
        preds = model(dummy_tensor, training=False)
        self.assertEqual(preds.shape, (1, 3))
        self.assertAlmostEqual(float(np.sum(preds.numpy())), 1.0, places=4)
        
    def test_inference_predictor_schema(self):
        if self.sample_img.exists():
            result = predict_disease(self.sample_img, compute_cam=False)
            
            self.assertIn("crop", result)
            self.assertIn("disease", result)
            self.assertIn("confidence", result)
            self.assertIn("confidence_percentage", result)
            self.assertIn("confidence_level", result)
            self.assertIn("is_confident", result)
            self.assertIn("clarification_needed", result)
            self.assertIn("top_predictions", result)
            self.assertGreaterEqual(len(result["top_predictions"]), 1)
            
    def test_confidence_threshold_categorization(self):
        predictor = AgriVisionPredictor()
        # High confidence check
        self.assertIn(predictor.predict(self.sample_img, compute_cam=False)["confidence_level"], ["High", "Moderate", "Low"])


if __name__ == "__main__":
    unittest.main()

