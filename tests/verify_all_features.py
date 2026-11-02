import sys
if sys.stdout.encoding != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')

import requests
import json
from pathlib import Path

BASE_URL = "http://127.0.0.1:8000"

def run_all_checks():
    print("=" * 65)
    print("🌾 AGRIVISION AGENT: FULL SYSTEM & FEATURE INTEGRITY VERIFICATION")
    print("=" * 65)

    # 1. Health
    r = requests.get(f"{BASE_URL}/health")
    assert r.status_code == 200
    print("✅ [1/12] Health Endpoint: Healthy (FastAPI 2.2.0 active)")

    # 2. Homepage & PWA
    r = requests.get(f"{BASE_URL}/")
    assert r.status_code == 200 and "AgriVision" in r.text
    r_man = requests.get(f"{BASE_URL}/manifest.json")
    r_sw = requests.get(f"{BASE_URL}/service-worker.js")
    assert r_man.status_code == 200 and r_sw.status_code == 200
    print("✅ [2/12] Web App & PWA: Loaded (HTML5 UI, Manifest, Service Worker)")

    # 3. Weather
    r = requests.get(f"{BASE_URL}/api/weather?location=Karnal,%20Haryana")
    assert r.status_code == 200
    w = r.json()
    print(f"✅ [3/12] Microclimate Weather: {w['location']} | {w['temperature_c']}°C | RH: {w['humidity_pct']}% | Spore Risk: {w['spore_germination_risk']}")

    # 4. Samples
    r = requests.get(f"{BASE_URL}/api/samples")
    assert r.status_code == 200
    samples = r.json().get("samples", [])
    print(f"✅ [4/12] Benchmark Samples: {len(samples)} crop disease specimens available")

    # 5. Mandi Market Intelligence
    r = requests.get(f"{BASE_URL}/api/mandi/forecast/wheat?district=Karnal")
    assert r.status_code == 200
    mf = r.json()
    print(f"✅ [5/12] APMC Mandi Forecast: Wheat @ {mf.get('target_district')} (Current: ₹{mf.get('current_price_per_qtl')}/Qtl | Forecast: ₹{mf.get('forecast_14d_price')}/Qtl) | Rec: {mf.get('recommendation')}")

    # 6. Haryana GIS Outbreak Map
    r = requests.get(f"{BASE_URL}/api/haryana/outbreak-map")
    assert r.status_code == 200
    gis = r.json()
    print(f"✅ [6/12] Haryana GIS Outbreak Telemetry: {len(gis.get('districts', []))} districts mapped")

    # 7. Soil NPK Fertilizer Engine
    r = requests.get(f"{BASE_URL}/api/soil/npk-calculator?crop=wheat&acres=1.5&soil_type=alluvial_loam&growth_stage=basal")
    assert r.status_code == 200
    npk = r.json()
    bags = npk.get("chemical_bags_needed", {})
    u_bags = bags.get("urea_45kg_bags", "N/A")
    d_bags = bags.get("dap_50kg_bags", "N/A")
    print(f"✅ [7/12] Precision NPK Engine: Wheat (1.5 Ac) -> Urea: {u_bags} bags (45kg) | DAP: {d_bags} bags (50kg)")

    # 8. Offline Agronomy Blocks
    r = requests.get(f"{BASE_URL}/api/haryana/offline-blocks")
    assert r.status_code == 200
    blocks = r.json().get("blocks", [])
    print(f"✅ [8/12] Offline Agronomy: {len(blocks)} Haryana administrative blocks available")

    # 9. Wheat Stripe Rust Neural Diagnosis
    with open("data/sample_images/wheat_stripe_rust.jpg", "rb") as f:
        r = requests.post(
            f"{BASE_URL}/api/diagnose",
            files={"file": ("wheat_leaf.jpg", f, "image/jpeg")},
            data={"field_acres": "1.5", "target_crop": "auto", "language": "en"}
        )
    assert r.status_code == 200
    d_wheat = r.json()
    assert d_wheat["crop"] == "Wheat", f"Expected Wheat, got {d_wheat['crop']}"
    assert "Rust" in d_wheat["disease"], f"Expected Rust, got {d_wheat['disease']}"
    print(f"✅ [9/12] Wheat Diagnosis: {d_wheat['crop']} — {d_wheat['disease']} ({d_wheat['confidence_percentage']}%) | Chem: {d_wheat['dosage_plan']['chemical_required']}")

    # 10. Rice Bacterial Leaf Blight Diagnosis
    with open("data/sample_images/rice_bacterial_leaf_blight.jpg", "rb") as f:
        r = requests.post(
            f"{BASE_URL}/api/diagnose",
            files={"file": ("rice_leaf.jpg", f, "image/jpeg")},
            data={"field_acres": "1.5", "target_crop": "auto", "language": "en"}
        )
    assert r.status_code == 200
    d_rice = r.json()
    assert d_rice["crop"] == "Rice", f"Expected Rice, got {d_rice['crop']}"
    print(f"✅ [10/12] Rice Diagnosis: {d_rice['crop']} — {d_rice['disease']} ({d_rice['confidence_percentage']}%)")

    # 11. Tomato Late Blight Diagnosis
    with open("data/sample_images/tomato_late_blight.jpg", "rb") as f:
        r = requests.post(
            f"{BASE_URL}/api/diagnose",
            files={"file": ("tomato_leaf.jpg", f, "image/jpeg")},
            data={"field_acres": "1.5", "target_crop": "Tomato", "language": "en"}
        )
    assert r.status_code == 200
    d_tomato = r.json()
    assert d_tomato["crop"] == "Tomato"
    print(f"✅ [11/12] Tomato Diagnosis: {d_tomato['crop']} — {d_tomato['disease']} ({d_tomato['confidence_percentage']}%)")

    # 12. Conversational Agronomy Chatbot
    r = requests.post(
        f"{BASE_URL}/api/chat",
        data={"message": "What is the recommended treatment for wheat yellow rust in Haryana?", "session_id": "demo_test"}
    )
    assert r.status_code == 200
    chat_resp = r.json().get("content", "")
    print(f"✅ [12/12] Autonomous AI Chatbot: Verified (Response: {chat_resp[:80]}...)")

    print("=" * 65)
    print("🏆 ALL 12/12 LIVE INTEGRATION CHECKS PASSED PERFECTLY!")
    print("=" * 65)

if __name__ == "__main__":
    run_all_checks()
