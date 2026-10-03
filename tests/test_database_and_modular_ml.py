"""
Unit and Integration tests for SQLite Database operations and Modular ML (app/database, app/ml).
"""

import unittest
from pathlib import Path
import sqlite3

from app.database.database import get_db_connection, init_db
from app.database.crud import save_prediction, get_recent_predictions, get_prediction_stats, save_chat_turn, get_chat_turns
from app.ml.model import build_custom_cnn, build_mobilenet_transfer_model
from app.ml.preprocessing import load_and_validate_image, apply_clahe, preprocess_for_inference
from app.ml.inference import predict_crop_disease


class TestDatabaseAndModularML(unittest.TestCase):
    
    def setUp(self):
        init_db()
        self.base_dir = Path(__file__).resolve().parent.parent
        self.sample_img_path = self.base_dir / "data" / "sample_images" / "tomato_early_blight.jpg"
        
    def test_database_save_and_retrieve_prediction(self):
        row_id = save_prediction(
            crop="Tomato",
            disease="Early Blight",
            confidence=0.945,
            crop_stage="Flowering",
            language="en",
            recommendation="Apply Mancozeb 75% WP @ 2.5g/L",
            weather_context="RH: 82%"
        )
        self.assertGreater(row_id, 0)
        
        recent = get_recent_predictions(limit=20)
        self.assertGreaterEqual(len(recent), 1)
        matched = [r for r in recent if r["prediction_id"] == row_id]
        self.assertEqual(len(matched), 1)
        latest = matched[0]
        self.assertEqual(latest["crop"], "Tomato")
        self.assertEqual(latest["disease"], "Early Blight")
        self.assertEqual(latest["crop_stage"], "Flowering")
        
    def test_database_stats(self):
        stats = get_prediction_stats()
        self.assertIn("total_scans", stats)
        self.assertIn("healthy_count", stats)
        self.assertIn("diseased_count", stats)
        self.assertIn("avg_confidence", stats)
        self.assertIn("top_diseases", stats)
        
    def test_database_chat_persistence(self):
        import uuid
        session_id = f"test_unit_session_{uuid.uuid4().hex[:8]}"
        turn_id = save_chat_turn(session_id, "user", "What is Early Blight?", "en")
        self.assertGreater(turn_id, 0)
        
        turns = get_chat_turns(session_id)
        self.assertEqual(len(turns), 1)
        self.assertEqual(turns[0]["content"], "What is Early Blight?")
        
    def test_modular_custom_cnn_construction(self):
        model = build_custom_cnn(num_classes=3, input_shape=(224, 224, 3))
        self.assertIsNotNone(model)
        self.assertEqual(model.output_shape, (None, 3))
        
    def test_modular_mobilenet_construction(self):
        model = build_mobilenet_transfer_model(num_classes=3, input_shape=(224, 224, 3), fine_tune_layers=0)
        self.assertIsNotNone(model)
        self.assertEqual(model.output_shape, (None, 3))
        
    def test_modular_preprocessing_and_inference(self):
        if self.sample_img_path.exists():
            img = load_and_validate_image(self.sample_img_path)
            clahe_img = apply_clahe(img)
            self.assertEqual(clahe_img.size, img.size)
            
            batch, resized = preprocess_for_inference(img)
            self.assertEqual(batch.shape, (1, 224, 224, 3))
            
            res = predict_crop_disease(self.sample_img_path, compute_gradcam=False)
            self.assertIn("crop", res)
            self.assertIn("disease", res)
            self.assertIn("confidence", res)
            self.assertIn("confidence_level", res)


if __name__ == "__main__":
    unittest.main()

