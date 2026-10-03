"""
Unit and Integration tests for Deep Learning Model, Inference Engine, and Grad-CAM.
"""

import unittest
from pathlib import Path
from PIL import Image
import numpy as np

from src.models.model_builder import build_transfer_learning_model
from src.models.inference import CropDiseaseClassifier, get_classifier
from src.database.db import save_scan, get_recent_scans, init_db


class TestModelInference(unittest.TestCase):
    
    def setUp(self):
        init_db()
        self.classifier = get_classifier()
        # Create synthetic leaf test image
        self.sample_img = Image.new("RGB", (224, 224), color=(40, 150, 45))
        
    def test_model_architecture(self):
        model = build_transfer_learning_model(num_classes=15, input_shape=(224, 224, 3))
        self.assertEqual(model.output_shape, (None, 15))
        self.assertEqual(model.name, "AgriVision_MobileNetV2")
        
    def test_classifier_prediction(self):
        pred = self.classifier.predict(self.sample_img, compute_cam=True)
        
        self.assertIn("predicted_index", pred)
        self.assertIn("crop", pred)
        self.assertIn("disease", pred)
        self.assertIn("confidence", pred)
        self.assertIn("confidence_percentage", pred)
        self.assertIn("top3_predictions", pred)
        self.assertEqual(len(pred["top3_predictions"]), 3)
        self.assertIn("is_healthy", pred)
        self.assertIn("is_confident", pred)
        
    def test_gradcam_generation(self):
        pred = self.classifier.predict(self.sample_img, compute_cam=True)
        self.assertIsNotNone(pred["gradcam_overlay"])
        self.assertIsInstance(pred["gradcam_overlay"], Image.Image)
        
    def test_scan_persistence_to_db(self):
        pred = self.classifier.predict(self.sample_img, compute_cam=False)
        scan_id = save_scan(
            crop_name=pred["crop"],
            condition=pred["disease"],
            is_healthy=pred["is_healthy"],
            confidence=pred["confidence"],
            top3_predictions=pred["top3_predictions"],
            ai_diagnosis="Automated DL verification scan.",
            treatment="Apply preventive biological fungicide.",
            prevention="Crop rotation and aeration.",
            language="en"
        )
        self.assertGreater(scan_id, 0)
        recent = get_recent_scans(limit=1)
        self.assertEqual(recent[0]["id"], scan_id)
        self.assertEqual(recent[0]["crop_name"], pred["crop"])


if __name__ == "__main__":
    unittest.main()

