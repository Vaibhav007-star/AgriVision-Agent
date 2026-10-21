"""
Unit tests for APMC Mandi 14-Day Price Forecaster and Haryana GIS Outbreak Telemetry.
"""

import sys
import unittest
import warnings
from pathlib import Path

# Ensure project root is in sys.path
BASE_DIR = Path(__file__).resolve().parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

# Suppress warnings
warnings.filterwarnings("ignore", category=DeprecationWarning)
warnings.filterwarnings("ignore", message=".*starlette.testclient.*")

with warnings.catch_warnings():
    warnings.simplefilter("ignore")
    from starlette.testclient import TestClient

from app.server import app
from app.services.mandi_forecaster import forecast_mandi_prices, HARYANA_COMMODITIES
from app.services.gis_outbreak_service import get_haryana_gis_outbreak_telemetry, HARYANA_DISTRICT_COORDINATES

client = TestClient(app)


class TestMandiForecastAndGIS(unittest.TestCase):

    def test_forecast_wheat_projection(self):
        data = forecast_mandi_prices(crop_key="wheat", district="Karnal", forecast_days=14)
        self.assertEqual(data["crop_key"], "wheat")
        self.assertEqual(data["target_district"], "Karnal")
        self.assertEqual(len(data["historical_series"]), 14)
        self.assertEqual(len(data["forecast_series"]), 14)
        self.assertIn(data["recommendation"], ["STRONG_HOLD", "HOLD", "SELL_NOW", "STAGGERED_SALE"])

        # Verify confidence bands
        for step in data["forecast_series"]:
            self.assertGreaterEqual(step["upper_bound"], step["projected_price"])
            self.assertLessEqual(step["lower_bound"], step["projected_price"])
            self.assertGreaterEqual(step["lower_bound"], data["msp_per_qtl"])

    def test_forecast_all_commodities(self):
        for key in HARYANA_COMMODITIES:
            res = forecast_mandi_prices(crop_key=key, district="Hisar")
            self.assertEqual(res["crop_key"], key)
            self.assertGreater(res["current_price_per_qtl"], 0)
            self.assertIn("title", res["advisory_en"])
            self.assertIn("title", res["advisory_hi"])

    def test_gis_outbreak_telemetry_structure(self):
        telemetry = get_haryana_gis_outbreak_telemetry()
        self.assertEqual(telemetry["state"], "Haryana")
        self.assertEqual(telemetry["total_districts"], 22)
        self.assertEqual(len(telemetry["districts"]), 22)
        self.assertGreaterEqual(telemetry["total_active_pathology_cases"], 22)

        district_names = {d["district"] for d in telemetry["districts"]}
        self.assertIn("Karnal", district_names)
        self.assertIn("Sirsa", district_names)
        self.assertIn("Hisar", district_names)
        self.assertIn("Yamunanagar", district_names)

        for d in telemetry["districts"]:
            self.assertIn("lat", d)
            self.assertIn("lon", d)
            self.assertIn(d["risk_level"], ["HIGH", "MODERATE", "LOW", "CLEAN"])
            self.assertTrue(d["pin_color"].startswith("#"))
            self.assertIn("kvk_alert_en", d)

    def test_mandi_forecast_api_endpoint(self):
        response = client.get("/api/mandi/forecast/wheat?district=Karnal&days=14")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["crop_key"], "wheat")
        self.assertEqual(len(data["forecast_series"]), 14)
        self.assertIn("advisory_en", data)

    def test_gis_outbreak_api_endpoint(self):
        response = client.get("/api/haryana/outbreak-map")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["state"], "Haryana")
        self.assertEqual(data["total_districts"], 22)


if __name__ == "__main__":
    unittest.main()
