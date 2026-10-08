"""
Unit and Integration tests for Services in app/services (Phase 6).
"""

import unittest

from app.services.weather import get_field_weather
from app.services.translation import translate_text, generate_bilingual_prescription
from app.services.voice import is_voice_available, text_to_speech, speech_to_text


class TestAppServices(unittest.TestCase):
    
    def test_field_weather_service(self):
        w = get_field_weather("Nagpur, India")
        self.assertEqual(w["location"], "Nagpur, India")
        self.assertIn("temperature_c", w)
        self.assertIn("humidity_pct", w)
        self.assertIn("spore_germination_risk", w)
        
    def test_translation_service_terms(self):
        self.assertEqual(translate_text("Tomato", "hi"), "टमाटर (Tomato)")
        self.assertEqual(translate_text("Early Blight", "hi"), "अगेती झुलसा रोग (Early Blight)")
        self.assertEqual(translate_text("Tomato", "en"), "Tomato")
        
    def test_bilingual_prescription_generator(self):
        dosage = {"water_volume_liters": 200, "sprayer_tanks_15L": 13.3, "chemical_required": "Mancozeb 2.5g/L"}
        hi_rx = generate_bilingual_prescription("Tomato", "Early Blight", 0.94, dosage_plan=dosage, target_lang="hi")
        self.assertIn("टमाटर", hi_rx)
        self.assertIn("झुलसा", hi_rx)
        
        en_rx = generate_bilingual_prescription("Tomato", "Early Blight", 0.94, dosage_plan=dosage, target_lang="en")
        self.assertIn("Tomato", en_rx)
        self.assertIn("Early Blight", en_rx)
        
    def test_voice_service_graceful_fallback(self):
        # Voice service should not raise unhandled exceptions
        tts_res = text_to_speech("Test speech synthesis")
        self.assertIn("success", tts_res)
        
        stt_res = speech_to_text(None)
        self.assertIn("success", stt_res)

    def test_mandi_haryana_markets(self):
        from app.services.mandi_market import get_mandi_intelligence
        crops = ["Tomato", "Potato", "Pepper Bell", "Wheat"]
        for crop in crops:
            res = get_mandi_intelligence(crop, acreage=1.5)
            self.assertIn("markets_table", res)
            for m in res["markets_table"]:
                self.assertEqual(m["state"], "Haryana", f"Market {m['mandi']} is not in Haryana")
            self.assertIn("economics", res)
            self.assertGreater(res["economics"]["gross_revenue_inr"], 0)


if __name__ == "__main__":
    unittest.main()

