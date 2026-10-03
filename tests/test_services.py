"""
Unit tests for Weather, Translation, and Voice Services (tests/test_services.py).
"""

import unittest
from app.services.weather import get_field_weather
from app.services.translation import translate_text, generate_bilingual_prescription
from app.services.voice import is_voice_available, text_to_speech, speech_to_text


class TestServices(unittest.TestCase):
    
    def test_weather_service(self):
        w = get_field_weather("Pune, India")
        self.assertEqual(w["location"], "Pune, India")
        self.assertIn("humidity_pct", w)
        self.assertIn("spore_germination_risk", w)
        
    def test_translation_service(self):
        self.assertEqual(translate_text("Tomato", "hi"), "टमाटर (Tomato)")
        rx = generate_bilingual_prescription("Tomato", "Early Blight", 0.94, target_lang="hi")
        self.assertIn("टमाटर", rx)
        
    def test_voice_service_fallback(self):
        res = text_to_speech("Test speech synthesis")
        self.assertIn("success", res)


if __name__ == "__main__":
    unittest.main()

