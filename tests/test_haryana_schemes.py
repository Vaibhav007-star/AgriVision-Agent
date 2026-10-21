"""
Test Suite for Haryana Government Schemes & CCS HAU Packages (Pillar 5)
"""

import pytest
from src.agronomy.haryana_schemes_rag import search_schemes_and_packages, HARYANA_GOVERNMENT_SCHEMES


def test_bhavantar_bharpai_search():
    res = search_schemes_and_packages("भावांतर भरपाई योजना")
    assert res["status"] == "MATCHED"
    assert len(res["matched_schemes"]) > 0
    assert "Bhavantar" in res["matched_schemes"][0]["title"]
    assert "Tomato" in res["matched_schemes"][0]["protected_base_prices"]


def test_mera_pani_meri_virasat():
    res = search_schemes_and_packages("mera pani meri virasat 7000 subsidy")
    assert res["status"] == "MATCHED"
    assert any("मेरा पानी" in s["title"] for s in res["matched_schemes"])


def test_solar_pump_kusum():
    res = search_schemes_and_packages("kusum solar tubewell pump")
    assert res["status"] == "MATCHED"
    assert any("कुसुम" in s["title"] for s in res["matched_schemes"])


def test_hau_variety_search():
    res = search_schemes_and_packages("WH-1105 wheat variety")
    assert res["status"] == "MATCHED"
    assert res["recommended_varieties"] is not None
    assert any(v["code"] == "WH-1105" for v in res["recommended_varieties"]["varieties"])

