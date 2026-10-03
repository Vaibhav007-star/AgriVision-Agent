"""
Unit tests for SQLite Database Schema and CRUD Operations (tests/test_database.py).
"""

import unittest
import uuid
from app.database.database import init_db
from app.database.crud import save_prediction, get_recent_predictions, get_prediction_stats, save_chat_turn, get_chat_turns


class TestDatabase(unittest.TestCase):
    
    def setUp(self):
        init_db()
        
    def test_save_and_retrieve_prediction(self):
        pid = save_prediction(
            crop="Tomato",
            disease="Early Blight",
            confidence=0.94,
            crop_stage="Vegetative",
            language="en",
            recommendation="Test recommendation"
        )
        self.assertGreater(pid, 0)
        recent = get_recent_predictions(limit=5)
        self.assertGreaterEqual(len(recent), 1)
        
    def test_prediction_stats(self):
        stats = get_prediction_stats()
        self.assertIn("total_scans", stats)
        self.assertIn("healthy_count", stats)
        self.assertIn("avg_confidence", stats)
        
    def test_chat_persistence(self):
        session_id = f"test_session_{uuid.uuid4().hex[:8]}"
        cid = save_chat_turn(session_id, "user", "Hello AgriVision", "en")
        self.assertGreater(cid, 0)
        turns = get_chat_turns(session_id)
        self.assertEqual(len(turns), 1)
        self.assertEqual(turns[0]["content"], "Hello AgriVision")


if __name__ == "__main__":
    unittest.main()

