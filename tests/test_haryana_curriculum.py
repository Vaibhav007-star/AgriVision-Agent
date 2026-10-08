"""
Automated Unit Tests for Haryana Agricultural Profile, Stepwise GPU Models, and REST Endpoints.
"""

import unittest
from pathlib import Path
from starlette.testclient import TestClient

from app.server import app
from src.data.haryana_agricultural_profile import (
    HARYANA_DISTRICTS,
    HARYANA_REGIONAL_BELTS,
    get_all_districts,
    get_district_info,
    get_crops_by_district,
    get_districts_by_crop,
    get_crop_profile_for_location
)

client = TestClient(app)


class TestHaryanaAgriculturalSystem(unittest.TestCase):

    def test_all_22_districts_present(self):
        districts = get_all_districts()
        self.assertEqual(len(districts), 22)
        expected_sample = ["Ambala", "Bhiwani", "Fatehabad", "Hisar", "Karnal", "Kurukshetra", "Sirsa", "Sonipat"]
        for d in expected_sample:
            self.assertIn(d, districts)

    def test_district_info_content(self):
        karnal = get_district_info("Karnal")
        self.assertIsNotNone(karnal)
        self.assertEqual(karnal["belt"], "North-East")
        self.assertIn("Wheat", karnal["crops"])
        self.assertIn("Paddy", karnal["crops"])
        self.assertIn("Gharaunda", karnal["main_cities"])

        hisar = get_district_info("Hisar")
        self.assertIsNotNone(hisar)
        self.assertEqual(hisar["belt"], "Western / South-Western")
        self.assertIn("Cotton", hisar["crops"])
        self.assertIn("Hansi", hisar["main_cities"])

    def test_districts_by_crop_query(self):
        wheat_districts = get_districts_by_crop("Wheat")
        self.assertGreaterEqual(len(wheat_districts), 20)
        self.assertIn("Karnal", wheat_districts)
        self.assertIn("Hisar", wheat_districts)

        cotton_districts = get_districts_by_crop("Cotton")
        self.assertIn("Sirsa", cotton_districts)
        self.assertIn("Fatehabad", cotton_districts)
        self.assertIn("Hisar", cotton_districts)

        sugarcane_districts = get_districts_by_crop("Sugarcane")
        self.assertIn("Yamunanagar", sugarcane_districts)
        self.assertIn("Karnal", sugarcane_districts)

    def test_location_matcher(self):
        # Match by district
        res = get_crop_profile_for_location("Sonipat, Haryana")
        self.assertEqual(res["matched_district"], "Sonipat")
        self.assertIn("Baby Corn", res["common_crops"])

        # Match by city/town
        res2 = get_crop_profile_for_location("Gharaunda Center")
        self.assertEqual(res2["matched_district"], "Karnal")

    def test_api_haryana_districts(self):
        response = client.get("/api/haryana/districts")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["state"], "Haryana")
        self.assertEqual(data["total_districts"], 22)
        self.assertIn("Karnal", data["districts"])

    def test_api_haryana_crops(self):
        response = client.get("/api/haryana/crops")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn("crops", data)
        self.assertIn("Wheat", data["crops"])
        self.assertIn("Cotton", data["crops"])

    def test_api_haryana_training_curriculum(self):
        response = client.get("/api/haryana/training-curriculum")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn("steps_completed", data)
        self.assertEqual(len(data["steps_completed"]), 6)
        # Verify first step is Wheat
        self.assertEqual(data["steps_completed"][0]["crop"], "wheat")
        self.assertGreater(data["steps_completed"][0]["best_val_acc"], 90.0)

    def test_master_model_checkpoint_exists(self):
        pt_path = Path("models/haryana_models/haryana_master_multicrop_gpu.pt")
        map_path = Path("models/haryana_models/haryana_class_map.json")
        self.assertTrue(pt_path.exists())
        self.assertTrue(map_path.exists())


if __name__ == "__main__":
    unittest.main()
