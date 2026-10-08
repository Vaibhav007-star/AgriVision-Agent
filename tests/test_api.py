"""
Automated unit tests for AgriVision FastAPI Web Application and REST Endpoints.
"""

import unittest
from starlette.testclient import TestClient
from pathlib import Path

from app.server import app

client = TestClient(app)


class TestWebApiEndpoints(unittest.TestCase):
    
    def test_serve_home_html(self):
        response = client.get("/")
        self.assertEqual(response.status_code, 200)
        self.assertIn("text/html", response.headers.get("content-type", ""))
        self.assertIn("AgriVision", response.text)
        self.assertIn("Nurturing Nature", response.text)
        
    def test_get_samples_api(self):
        response = client.get("/api/samples")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn("samples", data)
        self.assertIsInstance(data["samples"], list)
        if data["samples"]:
            sample = data["samples"][0]
            self.assertIn("id", sample)
            self.assertIn("crop", sample)
            self.assertIn("thumbnail", sample)
            
    def test_get_weather_api(self):
        response = client.get("/api/weather")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["location"], "Karnal, Haryana")
        self.assertIn("temperature_c", data)
        self.assertIn("humidity_pct", data)
        self.assertIn("spore_germination_risk", data)
        self.assertIn(data["spore_germination_risk"], ["High", "Moderate", "Low"])
        
    def test_get_stats_api(self):
        response = client.get("/api/stats")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn("total_scans", data)
        self.assertIn("healthy_count", data)
        
    def test_get_history_api(self):
        response = client.get("/api/history?limit=5")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn("history", data)
        self.assertIsInstance(data["history"], list)
        
    def test_post_chat_api(self):
        response = client.post(
            "/api/chat",
            data={
                "message": "What is Tomato Early Blight and how to treat it?",
                "language": "en"
            }
        )
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["role"], "assistant")
        self.assertIn("content", data)
        self.assertGreater(len(data["content"]), 10)

    def test_get_mandi_rates_haryana_only(self):
        """Verifies that all returned APMC mandis are strictly from Haryana state."""
        crops = ["Tomato", "Potato", "Pepper Bell", "Wheat"]
        for c in crops:
            response = client.get(f"/api/market-rates?crop={c}&acres=2.0")
            self.assertEqual(response.status_code, 200)
            data = response.json()
            self.assertIn("markets_table", data)
            self.assertGreater(len(data["markets_table"]), 0)
            for m in data["markets_table"]:
                self.assertEqual(m["state"], "Haryana", f"Market {m['mandi']} is not in Haryana!")
            states = set(m["state"] for m in data["markets_table"])
            self.assertEqual(states, {"Haryana"})
        
    def test_post_diagnose_sample_api(self):
        response = client.post(
            "/api/diagnose",
            data={
                "sample_id": "tomato_early_blight",
                "field_acres": 2.0,
                "crop_stage": "Flowering Stage",
                "location": "Karnal, Haryana",
                "language": "en"
            }
        )
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue(data.get("success", False))
        self.assertIn("crop", data)
        self.assertIn("disease", data)
        self.assertIn("confidence", data)
        self.assertIn("images", data)
        self.assertIn("original", data["images"])
        self.assertIn("foliage_mask", data["images"])
        self.assertIn("dosage_plan", data)
        self.assertIn("prescription", data)
        self.assertEqual(data["dosage_plan"]["water_volume_liters"], 400.0)
        self.assertIn("mandi_market", data)
        self.assertEqual(data["mandi_market"]["markets_table"][0]["state"], "Haryana")


if __name__ == "__main__":
    unittest.main()

