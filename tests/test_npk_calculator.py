"""
Test Suite for N-P-K Soil & Fertilizer Dosing Calculator (Pillar 4)
"""

import pytest
from src.agronomy.npk_calculator import calculate_fertilizer_dosage, CROP_NPK_STANDARDS, NUTRIENT_DEFICIENCY_GUIDE


def test_wheat_basal_npk():
    res = calculate_fertilizer_dosage(
        crop_name="wheat",
        acres=2.0,
        soil_type="alluvial_loam",
        growth_stage="basal"
    )
    assert res["status"] == "SUCCESS"
    assert res["acres"] == 2.0
    assert res["chemical_bags_needed"]["dap_50kg_bags"] > 0
    assert res["chemical_bags_needed"]["mop_potash_50kg_bags"] > 0
    assert res["organic_alternatives"]["vermicompost_tonnes"] == 3.0


def test_paddy_tillering_split():
    res = calculate_fertilizer_dosage(
        crop_name="paddy",
        acres=1.0,
        soil_type="clayey_lowland",
        growth_stage="tillering"
    )
    assert res["status"] == "SUCCESS"
    # Tillering split in paddy needs only top-dressed Nitrogen (Urea), no DAP/MOP
    assert res["chemical_bags_needed"]["dap_50kg_bags"] == 0.0
    assert res["chemical_bags_needed"]["mop_potash_50kg_bags"] == 0.0
    assert res["chemical_bags_needed"]["urea_45kg_bags"] > 0


def test_deficiency_triage_nitrogen():
    res = calculate_fertilizer_dosage(
        crop_name="wheat",
        acres=1.5,
        deficiency_observed="nitrogen"
    )
    triage = res["deficiency_triage"]
    assert triage is not None
    assert "Nitrogen" in triage["element"]
    assert "2% Urea" in triage["emergency_spray"]


def test_deficiency_triage_zinc():
    res = calculate_fertilizer_dosage(
        crop_name="paddy",
        acres=2.5,
        deficiency_observed="zinc"
    )
    triage = res["deficiency_triage"]
    assert triage is not None
    assert "Zinc" in triage["element"]
    assert "खैरा" in triage["vernacular_name"]
    assert "Zinc Sulphate" in triage["emergency_spray"]
