"""
Unit and Integration tests for LangGraph Agentic Workflow, State Machine, and Tools.
"""

import unittest

from src.agent.graph import run_agent_workflow, build_agrivision_agent
from src.tools.weather_tool import get_weather_data
from src.tools.agri_tools import calculate_field_dosage
from src.agent.llm_factory import get_llm


class TestAgentWorkflow(unittest.TestCase):
    
    def test_weather_tool(self):
        w = get_weather_data("Nagpur, India")
        self.assertIn("temperature_c", w)
        self.assertIn("humidity_pct", w)
        self.assertIn("spore_germination_risk", w)
        
    def test_dosage_tool(self):
        d = calculate_field_dosage("Tomato", "Early Blight", area_acres=2.0)
        self.assertEqual(d["field_area_acres"], 2.0)
        self.assertEqual(d["water_volume_liters"], 400.0)
        self.assertIn("chemical_required", d)
        
    def test_llm_factory(self):
        llm = get_llm()
        self.assertIsNotNone(llm)
        
    def test_high_confidence_agent_flow(self):
        result = run_agent_workflow(
            crop="Tomato",
            disease="Early Blight",
            confidence=0.94,
            field_acres=1.5,
            location="Pune, India",
            language="en"
        )
        self.assertEqual(result["status"], "completed")
        self.assertTrue(result["is_confident"])
        self.assertGreater(len(result["reasoning_steps"]), 3)
        self.assertIn("final_prescription", result)
        self.assertIn("biological_controls", result["final_prescription"])
        self.assertIn("field_dosage", result["final_prescription"])
        
    def test_low_confidence_clarification_flow(self):
        result = run_agent_workflow(
            crop="Potato",
            disease="Late Blight",
            confidence=0.45, # Below 0.60 threshold
            language="en"
        )
        self.assertEqual(result["status"], "completed")
        self.assertFalse(result["is_confident"])
        self.assertIn("Clarification Node", result["reasoning_steps"][-1])


if __name__ == "__main__":
    unittest.main()

