"""
Unit tests for Bilingual Translation, Real-Time Weather sync, and SQLite Chat persistence.
"""

import unittest

from src.utils.translation import (
    translate_crop_name,
    translate_disease_name,
    generate_hindi_advisory
)
from src.tools.weather_tool import get_weather_data
from src.database.db import save_chat_message, get_chat_history, init_db


class TestBilingualAndWeather(unittest.TestCase):
    
    def setUp(self):
        init_db()
        
    def test_crop_translation(self):
        self.assertIn("टमाटर", translate_crop_name("Tomato", "hi"))
        self.assertIn("आलू", translate_crop_name("Potato", "hi"))
        self.assertEqual(translate_crop_name("Tomato", "en"), "Tomato")
        
    def test_disease_translation(self):
        self.assertIn("झुलसा", translate_disease_name("Early Blight", "hi"))
        self.assertIn("गेरुआ", translate_disease_name("Common Rust", "hi"))
        
    def test_hindi_advisory_generation(self):
        dosage = {"water_volume_liters": 200, "sprayer_tanks_15L": 13.3, "chemical_required": "Mancozeb 2.5g/L"}
        adv = generate_hindi_advisory("Tomato", "Early Blight", 0.94, dosage_plan=dosage, weather_risk="High")
        self.assertIn("टमाटर", adv)
        self.assertIn("झुलसा", adv)
        self.assertIn("जैविक उपाय", adv)
        
    def test_weather_live_sync(self):
        w = get_weather_data("Bhopal, India")
        self.assertEqual(w["location"], "Bhopal, India")
        self.assertIn(w["spore_germination_risk"], ["High", "Moderate", "Low"])
        self.assertIn("spray_recommendation", w)
        
    def test_chat_persistence(self):
        test_session = "test_farmer_session_123"
        msg_id = save_chat_message(
            session_id=test_session,
            role="user",
            content="टमाटर में झुलसा रोग का क्या करें?",
            language="hi"
        )
        self.assertGreater(msg_id, 0)
        history = get_chat_history(session_id=test_session, limit=5)
        self.assertGreater(len(history), 0)
        self.assertEqual(history[-1]["content"], "टमाटर में झुलसा रोग का क्या करें?")


if __name__ == "__main__":
    unittest.main()

