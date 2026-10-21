"""
Test Suite for Microclimate Disease Triangle Outbreak Predictor (Pillar 7)
"""

import pytest
from src.agronomy.disease_triangle_engine import calculate_disease_triangle


def test_yellow_rust_high_risk():
    # Ideal conditions for yellow rust: 15°C, 92% RH, 9 hrs leaf wetness
    res = calculate_disease_triangle(
        crop="wheat",
        current_temp=15.0,
        relative_humidity=92.0,
        leaf_wetness_hours=9.0
    )
    assert res["status"] == "SUCCESS"
    assert res["composite_risk_pct"] >= 70.0
    assert res["alert_level"] == "HIGH_ALERT"
    assert "Yellow Rust" in res["monitored_disease"]
    assert len(res["five_day_trajectory"]) == 5


def test_favorable_clear_conditions():
    # Hot, dry conditions: 38°C, 25% RH, 0 hr leaf wetness
    res = calculate_disease_triangle(
        crop="wheat",
        current_temp=38.0,
        relative_humidity=25.0,
        leaf_wetness_hours=0.0
    )
    assert res["status"] == "SUCCESS"
    assert res["composite_risk_pct"] < 45.0
    assert res["alert_level"] == "FAVORABLE_CLEAR"
