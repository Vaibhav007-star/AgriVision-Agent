"""
Test Suite for Vernacular Voice & Dialect Parsing Engine (Pillar 1)
"""

import pytest
from src.nlp.dialect_voice_parser import parse_voice_query, detect_crop, detect_district


def test_hindi_wheat_yellow_rust():
    query = "मेरी कनक में पीला रतुआ आ गया है, क्या समाधान है?"
    res = parse_voice_query(query, district_hint="Karnal")
    assert res["status"] == "DIAGNOSIS_MATCHED"
    assert res["crop"] == "Wheat"
    assert "Yellow / Stripe Rust" in res["disease_detected"]
    assert "प्रोपिकोनाजोल" in res["spoken_hi"]
    assert "टिल्ट" in res["spoken_haryanvi"]
    assert res["confidence"] > 0.8


def test_haryanvi_dialect_query():
    query = "म्हारी कनक के पत्ते पीले होगे, के दवाई छिड़कूं?"
    res = parse_voice_query(query, district_hint="Hisar")
    assert res["status"] == "DIAGNOSIS_MATCHED"
    assert res["crop"] == "Wheat"
    assert "Yellow / Stripe Rust" in res["disease_detected"]
    assert "म्हारी कनक म पीला रतुआ का अटैक सै" in res["spoken_haryanvi"]


def test_paddy_bacterial_blight():
    query = "धान में पत्ती झुलसा का रोग दिख रहा है"
    res = parse_voice_query(query, district_hint="Kaithal")
    assert res["status"] == "DIAGNOSIS_MATCHED"
    assert "Paddy" in res["crop"]
    assert "Bacterial Leaf Blight" in res["disease_detected"]
    assert "कॉपर ऑक्सीक्लोराइड" in res["spoken_hi"]


def test_hinglish_cotton_pink_bollworm():
    query = "narma me gulabi sundi keeda lag gya sirsa me"
    res = parse_voice_query(query)
    assert res["status"] == "DIAGNOSIS_MATCHED"
    assert res["crop"] == "Cotton"
    assert "Pink Bollworm" in res["disease_detected"]
    assert res["district"] == "Sirsa"
    assert res["severity"] == "CRITICAL"


def test_tomato_early_blight():
    query = "tamatar ke patte par kale gol dhabbe hain"
    res = parse_voice_query(query, district_hint="Gharaunda")
    assert res["status"] == "DIAGNOSIS_MATCHED"
    assert res["crop"] == "Tomato"
    assert "Early Blight" in res["disease_detected"]
    assert "मैंकोजेब" in res["spoken_hi"]


def test_general_advice_fallback():
    query = "गन्ने की खेती के बारे में जानकारी"
    res = parse_voice_query(query)
    assert res["status"] == "GENERAL_ADVICE"
    assert res["crop"] == "Sugarcane"
    assert res["disease_detected"] is None
    assert "spoken_haryanvi" in res


def test_unrecognized_query():
    query = "मौसम कैसा रहेगा आज"
    res = parse_voice_query(query)
    assert res["status"] == "UNRECOGNIZED"
    assert "फसल का नाम" in res["spoken_hi"]

