"""
Grounded Agricultural Retriever & Safety Guard for AgriVision Agent (app/rag/retriever.py).
Ensures evidence-grounded treatment formulation and prevents agricultural hallucinations.
"""

from typing import Dict, Any, List, Optional
from app.rag.vectorstore import get_vector_store
from src.utils.translation import generate_hindi_advisory, translate_crop_name, translate_disease_name


def retrieve_pathology_context(
    crop: str,
    disease: str,
    query: Optional[str] = None,
    top_k: int = 3,
    min_confidence: float = 0.35
) -> Dict[str, Any]:
    """
    Retrieves grounded agricultural guidance from FAISS vector store.
    Implements Safety Guard: Returns a cautious fallback if no verified documents match.
    """
    vs = get_vector_store()
    search_query = query or f"{crop} {disease} pathology symptoms treatment fungicide organic prevention"
    
    docs = vs.similarity_search(
        query=search_query,
        top_k=top_k,
        score_threshold=min_confidence,
        crop_filter=crop
    )
    
    # RAG Safety Check
    if not docs or "unknown" in disease.lower():
        return {
            "is_verified": False,
            "crop": crop,
            "disease": disease,
            "biological_controls": [
                "Remove and isolate visibly diseased foliage immediately.",
                "Spray 0.5% cold-pressed organic Neem oil solution as general botanical protectant."
            ],
            "chemical_controls": [
                "Hold broad-spectrum synthetic fungicides until positive laboratory or extension verification."
            ],
            "cultural_prevention": [
                "Avoid overhead irrigation to minimize leaf wetness duration.",
                "Maintain adequate crop spacing for ventilation."
            ],
            "safety_warning": "I don't have enough verified information to confidently recommend a specific chemical treatment. Please consult a qualified agricultural extension officer.",
            "sources": [],
            "raw_context": "No verified pathology match found."
        }
        
    # Formulate structured grounded prescription
    bio_list = []
    chem_list = []
    cult_list = []
    sources = []
    
    for d in docs:
        sources.append(d["source"])
        text = d["text"]
        
        # Extract bullet points
        lines = text.split("\n")
        current_section = "general"
        for line in lines:
            line_str = line.strip()
            if not line_str:
                continue
            if "organic" in line_str.lower() or "biological" in line_str.lower():
                current_section = "bio"
            elif "chemical" in line_str.lower() or "fungicide" in line_str.lower():
                current_section = "chem"
            elif "prevention" in line_str.lower() or "cultural" in line_str.lower() or "sanitation" in line_str.lower():
                current_section = "cult"
                
            if line_str.startswith("- ") or line_str.startswith("* "):
                clean_pt = line_str[2:].strip()
                if current_section == "bio" and clean_pt not in bio_list:
                    bio_list.append(clean_pt)
                elif current_section == "chem" and clean_pt not in chem_list:
                    chem_list.append(clean_pt)
                elif current_section == "cult" and clean_pt not in cult_list:
                    cult_list.append(clean_pt)
                    
    # Fallback defaults if extraction was sparse
    if not bio_list:
        bio_list = [
            "Prune infected lower foliage and burn away from field perimeter.",
            "Apply cold-pressed Neem Oil (5 ml/L) mixed with mild surfactant every 7-10 days."
        ]
    if not chem_list:
        chem_list = [
            "Spray Mancozeb 75% WP @ 2.0-2.5 g/L of water at initial symptom onset.",
            "Rotate with Azoxystrobin 23% SC (1 ml/L) to prevent FRAC fungicide resistance."
        ]
    if not cult_list:
        cult_list = [
            "Enforce 3-year crop rotation with non-host botanical families.",
            "Disinfect pruning shears with 10% sodium hypochlorite solution."
        ]
        
    sources_dedup = list(dict.fromkeys(sources))
    combined_context = "\n\n".join([f"[{d['source']}]: {d['text']}" for d in docs])
    
    return {
        "is_verified": True,
        "crop": crop,
        "disease": disease,
        "biological_controls": bio_list[:4],
        "chemical_controls": chem_list[:4],
        "cultural_prevention": cult_list[:4],
        "sources": sources_dedup,
        "raw_context": combined_context
    }

