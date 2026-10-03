"""
Unit and Integration tests for LangGraph Agent in app/agent (Phase 5).
"""

import unittest

from app.agent.tools.weather_tool import get_weather_data
from app.agent.tools.crop_info_tool import get_crop_info
from app.agent.tools.disease_info_tool import get_disease_info
from app.agent.tools.dosage_tool import calculate_spray_dosage
from app.agent.graph import run_agent_workflow


class TestAppAgent(unittest.TestCase):
    
    def test_weather_tool(self):
        w = get_weather_data("Bhopal, India")
        self.assertIn("temperature_c", w)
        self.assertIn("humidity_pct", w)
        self.assertIn("spore_germination_risk", w)
        self.assertIn(w["spore_germination_risk"], ["High", "Moderate", "Low"])
        
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
        self.assertIn("Mancozeb", d["chemical_required"])
        
    def test_high_confidence_agent_workflow(self):
        result = run_agent_workflow(
            crop="Tomato",
            disease="Early Blight",
            confidence=0.94,
            field_acres=1.5,
            crop_stage="Flowering Stage",
            language="en"
        )
        self.assertTrue(result["is_confident"])
        self.assertFalse(result["clarification_needed"])
        self.assertGreater(len(result["reasoning_steps"]), 3)
        self.assertIn("final_prescription", result)
        self.assertIn("dosage_plan", result)
        
    def test_low_confidence_clarification_branch(self):
        result = run_agent_workflow(
            crop="Tomato",
            disease="Early Blight",
            confidence=0.45,  # Below 60% threshold
            field_acres=1.0,
            language="en"
        )
        self.assertFalse(result["is_confident"])
        self.assertTrue(result["clarification_needed"])
        self.assertIn("clearer", result["final_response"].lower())


if __name__ == "__main__":
    unittest.main()

