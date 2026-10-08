"""
FastAPI Full-Stack Server for AgriVision Agent.
Serves the modern Zenze-inspired responsive web application and provides high-performance
asynchronous REST APIs for Computer Vision, Deep Learning, FAISS RAG, LangGraph Agent, and SQLite.
"""

import os
import sys

# Ensure UTF-8 output encoding across Windows terminals
try:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    if hasattr(sys.stderr, "reconfigure"):
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

# Silence low-level TensorFlow and oneDNN C++ messages for a clean terminal
os.environ["TF_CPP_MIN_LOG_LEVEL"] = "3"
os.environ["TF_ENABLE_ONEDNN_OPTS"] = "0"

from typing import Optional, List, Dict, Any
import io
import base64
from pathlib import Path

from fastapi import FastAPI, File, UploadFile, Form, HTTPException, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, JSONResponse, FileResponse
from PIL import Image

# Ensure project root is in sys.path
BASE_DIR = Path(__file__).resolve().parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from app.ml.preprocessing import load_and_validate_image, apply_clahe, preprocess_for_inference
from app.ml.inference import predict_crop_disease
from app.agent.graph import run_agent_workflow
from app.agent.tools.weather_tool import get_weather_data
from app.database.crud import (
    save_prediction,
    get_recent_predictions,
    get_prediction_stats,
    save_chat_turn,
    get_chat_turns
)
from app.rag.vectorstore import get_vector_store
from app.rag.retriever import retrieve_pathology_context
from src.utils.image_processing import segment_leaf_mask, compute_digital_lcc
from src.utils.dataset import get_available_samples
from app.services.predictive_pathology import calculate_disease_outbreak_risk, evaluate_climate_spray_window
from app.services.mandi_market import get_mandi_intelligence, MANDI_DATABASE

app = FastAPI(
    title="AgriVision Agent — Precision Agricultural Intelligence",
    description="Autonomous Agentic AI Crop Disease Detection, Diagnosis & Agronomic Advisory System",
    version="2.0.0"
)

# Enable CORS for local development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount Static Assets and Jinja Templates
STATIC_DIR = BASE_DIR / "app" / "static"
TEMPLATES_DIR = BASE_DIR / "app" / "templates"
STATIC_DIR.mkdir(parents=True, exist_ok=True)
TEMPLATES_DIR.mkdir(parents=True, exist_ok=True)

app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")
templates = Jinja2Templates(directory=str(TEMPLATES_DIR))


def pil_to_base64(img: Image.Image, format: str = "JPEG") -> str:
    """Encodes a PIL Image to a base64 data URI string."""
    buffered = io.BytesIO()
    img.save(buffered, format=format)
    encoded = base64.b64encode(buffered.getvalue()).decode("utf-8")
    return f"data:image/{format.lower()};base64,{encoded}"


@app.get("/manifest.json")
async def get_manifest():
    """Serves PWA Web App Manifest for mobile installation."""
    manifest_file = STATIC_DIR / "manifest.json"
    return FileResponse(manifest_file, media_type="application/manifest+json")


@app.get("/service-worker.js")
async def get_service_worker():
    """Serves PWA Service Worker with root scope permissions."""
    sw_file = STATIC_DIR / "service-worker.js"
    return FileResponse(
        sw_file,
        media_type="application/javascript",
        headers={"Service-Worker-Allowed": "/"}
    )


@app.get("/", response_class=HTMLResponse)
async def serve_home(request: Request):
    """Renders the main Zenze-inspired web application."""
    index_file = TEMPLATES_DIR / "index.html"
    with open(index_file, "r", encoding="utf-8") as f:
        return HTMLResponse(content=f.read())


@app.get("/favicon.ico", include_in_schema=False)
async def favicon():
    """Returns 204 No Content for favicon requests to prevent 404 terminal logs."""
    from fastapi import Response
    return Response(status_code=204)


@app.get("/api/samples")
async def list_benchmark_samples() -> Dict[str, Any]:
    """Returns available benchmark samples with preview thumbnails."""
    samples = get_available_samples()
    output = []
    
    for name, path in samples.items():
        try:
            pil_img = Image.open(path).convert("RGB")
            thumb = pil_img.copy()
            thumb.thumbnail((120, 120))
            thumb_b64 = pil_to_base64(thumb, format="JPEG")
            
            crop = "Tomato"
            if "Early" in name:
                cond = "Early Blight"
            elif "Late" in name:
                cond = "Late Blight"
            else:
                cond = "Healthy"
                
            output.append({
                "id": Path(path).stem,
                "label": name,
                "crop": crop,
                "condition": cond,
                "thumbnail": thumb_b64
            })
        except Exception:
            continue
            
    return {"samples": output}


@app.get("/api/weather")
async def get_weather(location: str = "Karnal, Haryana") -> Dict[str, Any]:
    """Returns microclimate environmental context and fungal spore risk."""
    return get_weather_data(location)


@app.post("/api/diagnose")
async def diagnose_leaf(
    file: Optional[UploadFile] = File(None),
    sample_id: Optional[str] = Form(None),
    field_acres: float = Form(1.5),
    crop_stage: str = Form("Vegetative Growth"),
    location: str = Form("Karnal, Haryana"),
    language: str = Form("en")
) -> Dict[str, Any]:
    """
    Complete end-to-end diagnostic pipeline:
    1. Load leaf image (Upload or Sample)
    2. OpenCV CLAHE & Foliage Segmentation
    3. MobileNetV2 Neural Inference & Top-3 Probabilities
    4. Grad-CAM Lesion Heatmap Generation
    5. LangGraph Multi-Node State Machine Execution
    6. Knapsack Tank Dosage & RAG Treatment Formulation
    7. SQLite Database Audit Logging
    """
    pil_image: Optional[Image.Image] = None
    image_name = "leaf_scan.jpg"
    
    if file and file.filename:
        image_bytes = await file.read()
        if not image_bytes:
            raise HTTPException(status_code=400, detail="Uploaded file is empty.")
        pil_image = Image.open(io.BytesIO(image_bytes)).convert("RGB")
        image_name = file.filename
    elif sample_id:
        samples = get_available_samples()
        matched_path = None
        for k, p in samples.items():
            if (k.lower() == sample_id.lower() or 
                Path(p).stem.lower() == sample_id.lower() or 
                k.replace(" ", "_").lower() == sample_id.lower() or
                sample_id.lower() in k.lower()):
                matched_path = p
                break
        if not matched_path:
            direct_path = BASE_DIR / "data" / "sample_images" / f"{sample_id}.jpg"
            if direct_path.exists():
                matched_path = str(direct_path)
            else:
                raise HTTPException(status_code=404, detail=f"Sample '{sample_id}' not found.")
        pil_image = Image.open(matched_path).convert("RGB")
        image_name = f"{sample_id}.jpg"
    else:
        # Default fallback to tomato early blight sample
        sample_img = BASE_DIR / "data" / "sample_images" / "tomato_early_blight.jpg"
        if sample_img.exists():
            pil_image = Image.open(sample_img).convert("RGB")
        else:
            raise HTTPException(status_code=400, detail="Please upload a leaf image or select a benchmark sample.")

    # 1. Computer Vision Preprocessing
    clahe_image = apply_clahe(pil_image)
    seg_result = segment_leaf_mask(pil_image)
    
    # 2. Deep Learning Inference & Botanical OOD Guardrail
    inference_result = predict_crop_disease(pil_image, compute_gradcam=True)
    is_leaf = inference_result.get("is_leaf", True)
    leaf_val = inference_result.get("leaf_validation", {})
    
    crop = inference_result["crop"]
    disease = inference_result["disease"]
    confidence = inference_result["confidence"]
    
    # 3. LangGraph Autonomous Multi-Node Workflow
    agent_result = run_agent_workflow(
        crop=crop,
        disease=disease,
        confidence=confidence,
        field_acres=field_acres,
        location=location,
        crop_stage=crop_stage,
        language=language,
        is_leaf=is_leaf,
        leaf_validation=leaf_val
    )
    
    from app.agent.tools.dosage_tool import calculate_spray_dosage

    weather_data = agent_result.get("weather", {})
    
    # If not a leaf, STRICTLY suppress all chemical/biological fungicide & knapsack dosages
    if not is_leaf:
        final_prescription = None
        dosage_plan = None
        treatment_str = "Halted: Input image is NOT a crop leaf (Human or non-plant object detected)."
        prevention_str = "Upload a genuine leaf photo from Tomato, Potato, Pepper, Apple, or Corn crops."
    else:
        final_prescription = agent_result.get("final_prescription", {})
        dosage_plan = agent_result.get("dosage_plan", {})
        if not dosage_plan:
            dosage_plan = calculate_spray_dosage(crop, disease, field_acres=field_acres)
        treatment_str = "; ".join(final_prescription.get("chemical_controls", [])) if final_prescription else ""
        prevention_str = "; ".join(final_prescription.get("cultural_prevention", [])) if final_prescription else ""
    
    # 4. Save Record to SQLite
    prediction_id = save_prediction(
        crop=crop,
        disease=disease,
        confidence=confidence,
        crop_stage=crop_stage,
        language=language,
        recommendation=inference_result.get("advisory_message", ""),
        weather_context=f"{location} (RH: {weather_data.get('humidity_pct', 75)}%)" if is_leaf else "N/A",
        treatment=treatment_str,
        prevention=prevention_str,
        top3_predictions=inference_result.get("top_predictions", [])
    )
    
    # Prepare Image Base64 Data URIs
    orig_b64 = pil_to_base64(pil_image, format="JPEG")
    clahe_b64 = pil_to_base64(clahe_image, format="JPEG")
    gradcam_b64 = pil_to_base64(inference_result["gradcam_overlay"], format="JPEG") if inference_result.get("gradcam_overlay") else None
    mask_b64 = pil_to_base64(seg_result["segmented_image"], format="JPEG") if (seg_result and seg_result.get("segmented_image")) else None
    # 5. Digital IRRI Leaf Color Chart (LCC) Nitrogen Analysis
    lcc_result = compute_digital_lcc(pil_image) if is_leaf else None

    # 6. Predictive Pathology & Climate-Smart Safe Spray Window
    weather_dict = weather_data if isinstance(weather_data, dict) else {}
    temp_c = float(weather_dict.get("temperature_c", 26.5))
    humidity_val = int(weather_dict.get("humidity_pct", 75))
    rain_prob = int(weather_dict.get("rain_probability_pct", 35))
    wind_kmh = float(weather_dict.get("wind_speed_kmh", 10.5))

    predictive_risk = calculate_disease_outbreak_risk(
        crop=crop,
        disease=disease,
        temperature_c=temp_c,
        humidity_pct=humidity_val,
        rain_prob_pct=rain_prob
    ) if is_leaf else None

    spray_window = evaluate_climate_spray_window(
        temperature_c=temp_c,
        humidity_pct=humidity_val,
        rain_prob_pct=rain_prob,
        wind_speed_kmh=wind_kmh
    ) if is_leaf else None

    # 7. Mandi (APMC) Market Intelligence & Crop Economics
    mandi_data = get_mandi_intelligence(crop, acreage=field_acres) if is_leaf else None

    return {
        "success": True,
        "is_leaf": is_leaf,
        "leaf_validation": leaf_val,
        "prediction_id": prediction_id,
        "crop": crop,
        "disease": disease,
        "is_healthy": inference_result["is_healthy"],
        "confidence": confidence,
        "confidence_percentage": inference_result["confidence_percentage"],
        "confidence_level": inference_result["confidence_level"],
        "is_confident": inference_result["is_confident"],
        "advisory_message": inference_result["advisory_message"],
        "top_predictions": inference_result["top_predictions"],
        "lesion_percentage": seg_result["lesion_percentage"] if is_leaf else 0.0,
        "weather": weather_data if is_leaf else {},
        "dosage_plan": dosage_plan,
        "prescription": final_prescription,
        "lcc": lcc_result,
        "predictive_pathology": predictive_risk,
        "spray_window": spray_window,
        "mandi_market": mandi_data,
        "reasoning_steps": agent_result.get("reasoning_steps", []),
        "images": {
            "original": orig_b64,
            "clahe": clahe_b64,
            "gradcam": gradcam_b64,
            "foliage_mask": mask_b64
        }
    }


@app.get("/api/market-rates")
async def market_rates_endpoint(crop: str = "Tomato", acres: float = 1.5):
    """
    Returns live APMC Mandi commodity rates, arbitrage comparison, and farm economic projections.
    """
    return get_mandi_intelligence(crop, acreage=acres)


@app.post("/api/chat")
async def chat_endpoint(
    message: str = Form(...),
    language: str = Form("en"),
    session_id: str = Form("default_farmer_session")
) -> Dict[str, Any]:
    """
    Conversational Farmer Advisory endpoint powered by FAISS Vector RAG and SQLite memory.
    """
    if not message.strip():
        return {
            "role": "assistant",
            "content": "Please enter a question regarding crop disease, pest management, or treatment dosages."
        }
        
    save_chat_turn(session_id, "user", message, language=language)
    
    # Retrieve Grounded Knowledge from FAISS
    docs = []
    try:
        vs = get_vector_store()
        docs = vs.similarity_search(message, top_k=2)
    except Exception:
        docs = []
        
    is_hindi = language == "hi" or any('\u0900' <= char <= '\u097F' for char in message)
    
    if docs:
        best_doc = docs[0]
        context_snippet = best_doc["text"]
        source_name = best_doc.get("source", "Agricultural Pathology Manual")
        score = best_doc.get("score", 0.85)
        
        if is_hindi:
            reply = (
                f"🌾 **AgriVision विशेषज्ञ कृषक परामर्श:**\n\n"
                f"{context_snippet}\n\n"
                f"*(सत्यापित स्रोत: `{source_name}`)*"
            )
        else:
            reply = (
                f"🌾 **AgriVision Agronomic Advisory:**\n\n"
                f"{context_snippet}\n\n"
                f"*(Grounded Source: `{source_name}`, Relevance Score: {score:.2f})*"
            )
    else:
        if is_hindi:
            reply = "रोग की रोकथाम के लिए पौधों के बीच पर्याप्त दूरी रखें, पत्तियों को गीला रखने से बचें और गंभीर प्रकोप में स्थानीय कृषि विशेषज्ञ से संपर्क करें।"
        else:
            reply = "For effective prevention, ensure proper plant spacing, avoid prolonged leaf wetness, and consult local extension officers for severe outbreaks."
            
    save_chat_turn(session_id, "assistant", reply, language=language)
    
    return {
        "role": "assistant",
        "content": reply,
        "sources": [d.get("source") for d in docs] if docs else []
    }


@app.get("/api/history")
async def fetch_history(limit: int = 20) -> Dict[str, Any]:
    """Returns previous diagnostic scan records from SQLite."""
    records = get_recent_predictions(limit=limit)
    return {"history": records}


@app.get("/api/stats")
async def fetch_stats() -> Dict[str, Any]:
    """Returns aggregate telemetry metrics and disease incident breakdowns."""
    stats = get_prediction_stats()
    return stats


if __name__ == "__main__":
    import uvicorn
    try:
        if hasattr(sys.stdout, "reconfigure"):
            sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        if hasattr(sys.stderr, "reconfigure"):
            sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

    import socket
    def get_local_ip():
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("8.8.8.8", 80))
            ip = s.getsockname()[0]
            s.close()
            return ip
        except Exception:
            return "127.0.0.1"

    local_ip = get_local_ip()

    print("\n" + "=" * 70)
    print("[*] AgriVision Agent — Autonomous Precision Agriculture Web Platform")
    print("[+] Server is RUNNING at http://127.0.0.1:8000")
    print("")
    print("👉 OPEN IN BROWSER (Click or copy this link into your browser):")
    print("   http://localhost:8000")
    print("   http://127.0.0.1:8000")
    print("=" * 70 + "\n")
    uvicorn.run("app.server:app", host="127.0.0.1", port=8000, reload=False, log_level="info")
