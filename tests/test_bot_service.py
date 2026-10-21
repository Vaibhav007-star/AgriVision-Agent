"""
Unit tests for WhatsApp and Telegram AI Agri-Bot Service and Webhook Endpoints.
"""

import sys
import unittest
import warnings
from pathlib import Path

# Ensure project root is in sys.path
BASE_DIR = Path(__file__).resolve().parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

# Suppress Starlette deprecation warnings
warnings.filterwarnings("ignore", category=DeprecationWarning)
warnings.filterwarnings("ignore", message=".*starlette.testclient.*")

with warnings.catch_warnings():
    warnings.simplefilter("ignore")
    from starlette.testclient import TestClient

from app.server import app
from app.services.bot_service import AgriBotService

client = TestClient(app)


class TestAgriBotService(unittest.TestCase):

    def setUp(self):
        self.bot_service = AgriBotService()
        self.sample_img_path = BASE_DIR / "data" / "sample_images" / "tomato_early_blight.jpg"

    def test_text_greeting_query(self):
        res = self.bot_service.handle_message(sender_id="farmer_1", text="नमस्ते", language="hi")
        self.assertIn("message", res)
        self.assertIn("एग्रीविज़न", res["message"])

    def test_text_mandi_query(self):
        res = self.bot_service.handle_message(sender_id="farmer_2", text="आज का मंडी भाव क्या है?", language="hi", district="Karnal")
        self.assertIn("message", res)
        self.assertIn("मंडी भाव", res["message"])
        self.assertIn("Wheat", res["message"])

    def test_text_block_query(self):
        res = self.bot_service.handle_message(sender_id="farmer_3", text="मुझे करनाल के ब्लॉक बताएं", language="hi", district="Karnal")
        self.assertIn("message", res)
        self.assertIn("कृषि खंड", res["message"])

    def test_leaf_image_diagnosis(self):
        if self.sample_img_path.exists():
            with open(self.sample_img_path, "rb") as f:
                img_bytes = f.read()
            res = self.bot_service.handle_message(
                sender_id="farmer_4",
                image_bytes=img_bytes,
                language="hi",
                district="Karnal",
                acreage=2.0
            )
            self.assertIn(res["status"], ["diagnosed", "rejected"])
            self.assertIn("message", res)
            if res["status"] == "diagnosed":
                self.assertIn("HAU", res["message"])
                self.assertIn("स्प्रे गणना", res["message"])

    def test_bot_simulate_endpoint(self):
        payload = {
            "sender_id": "test_user_99",
            "text": "What is the price of wheat in Karnal mandi?",
            "language": "en",
            "district": "Karnal",
            "acreage": 1.5
        }
        response = client.post("/api/bot/simulate", json=payload)
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn("message", data)
        self.assertIn("Haryana APMC Mandi", data["message"])

    def test_telegram_webhook_endpoint(self):
        payload = {
            "update_id": 10001,
            "message": {
                "message_id": 1,
                "from": {"id": 123456, "first_name": "Ramesh"},
                "chat": {"id": 123456, "type": "private"},
                "text": "मंडी भाव",
            }
        }
        response = client.post("/api/bot/telegram/webhook", json=payload)
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue(data.get("ok"))
        self.assertEqual(data.get("method"), "sendMessage")
        self.assertIn("मंडी भाव", data.get("text", ""))

    def test_whatsapp_webhook_endpoint(self):
        form_data = {
            "From": "whatsapp:+919812345678",
            "Body": "राम-राम",
            "NumMedia": "0"
        }
        response = client.post("/api/bot/whatsapp/webhook", data=form_data)
        self.assertEqual(response.status_code, 200)
        self.assertIn("xml", response.headers.get("content-type", ""))
        self.assertIn("<Response>", response.text)
        self.assertIn("<Message>", response.text)


if __name__ == "__main__":
    unittest.main()
