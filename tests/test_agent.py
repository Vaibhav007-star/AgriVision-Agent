"""
Unit tests for LangGraph Agent State Machine and Tools (tests/test_agent.py).
"""

import unittest
from app.agent.tools.weather_tool import get_weather_data
from app.agent.tools.crop_info_tool import get_crop_info
from app.agent.tools.disease_info_tool import get_disease_info
from app.agent.tools.dosage_tool import calculate_spray_dosage
from app.agent.graph import run_agent_workflow


class TestAgent(unittest.TestCase):
    
    def test_weather_tool(self):
        w = get_weather_data("Bhopal, India")
        self.assertIn("temperature_c", w)
        self.assertIn("humidity_pct", w)
        self.assertIn("spore_germination_risk", w)
        
    def test_crop_info_tool(self):
        info = get_crop_info("Tomato")
        self.assertTrue(info["found"])
        self.assertEqual(info["family"], "Solanaceae")
        
    def test_disease_info_tool(self):
        info = get_disease_info("Tomato", "Early Blight")
        self.assertTrue(info["found"])
        self.assertIn("Alternaria solani", info["causal_agent"])
        
    def test_dosage_tool(self):
        d = calculate_spray_dosage("Tomato", "Early Blight", field_acres=2.0)
        self.assertEqual(d["water_volume_liters"], 400.0)
        self.assertEqual(d["sprayer_tanks_15L"], round(400.0 / 15.0, 1))
        
    def test_agent_graph_execution(self):
        res = run_agent_workflow("Tomato", "Early Blight", 0.92, field_acres=1.0)
        self.assertTrue(res["is_confident"])
        self.assertIn("final_prescription", res)
        self.assertGreater(len(res["reasoning_steps"]), 2)


if __name__ == "__main__":
    unittest.main()

