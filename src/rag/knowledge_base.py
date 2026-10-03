"""
Agricultural Knowledge Base Service for AgriVision Agent.
Provides structured diagnostic queries, RAG context retrieval,
and actionable agronomic prescriptions for the AI Agent and User Interface.
"""

from typing import Dict, Any, List, Optional
from src.rag.vector_store import get_vector_store


def query_rag(
    query: str,
    crop: Optional[str] = None,
    disease: Optional[str] = None,
    top_k: int = 3
) -> Dict[str, Any]:
    """
    Queries the vector database for agronomic context relevant to the user or agent prompt.
    """
    store = get_vector_store()
    results = store.search(query, crop=crop, disease=disease, top_k=top_k)
    
    combined_context = "\n\n---\n\n".join([r["text"] for r in results])
    return {
        "query": query,
        "results_count": len(results),
        "documents": results,
        "combined_context": combined_context
    }


def get_structured_prescriptions(
    crop: str,
    disease: str,
    weather_risk: str = "Moderate",
    language: str = "en"
) -> Dict[str, Any]:
    """
    Retrieves grounded, structured agronomic recommendations for a specific crop and disease diagnosis.
    """
    is_healthy = "healthy" in disease.lower()
    
    if is_healthy:
        return {
            "crop": crop,
            "condition": "Healthy",
            "is_healthy": True,
            "biological_controls": [
                "Maintain routine preventive spraying of Neem oil (3 ml/L) once a month.",
                "Apply balanced organic compost and vermicompost around root zones."
            ],
            "chemical_controls": [
                "No synthetic fungicides or bactericides required for healthy foliage."
            ],
            "cultural_prevention": [
                "Maintain uniform irrigation schedules avoiding waterlogging.",
                "Inspect lower leaves weekly for early signs of pathogen entry."
            ],
            "safety_guidelines": "Continue standard crop management and nutrient replenishment.",
            "hindi_summary": f"आपकी {crop} की फसल स्वस्थ है। कोई रासायनिक दवा डालने की आवश्यकता नहीं है। नियमित देखभाल जारी रखें।"
        }
        
    # Search RAG store for exact disease
    search_query = f"{crop} {disease} treatment biological control chemical fungicide prevention dosage"
    rag_data = query_rag(search_query, crop=crop, disease=disease, top_k=2)
    
    # Standard structured extraction based on pathology knowledge
    if "early blight" in disease.lower():
        bio = [
            "Spray pure cold-pressed Neem Seed Oil (5 ml/L + 1 ml liquid soap) every 7-10 days.",
            "Apply bio-fungicide Trichoderma viride / harzianum (5-10 g/L) to foliage and soil.",
            "Prune and destroy infected lower leaves (bottom 30 cm of plant canopy)."
        ]
        chem = [
            "Protective contact: Mancozeb 75% WP @ 2.5 g/L or Copper Oxychloride 50% WP @ 3.0 g/L.",
            "Curative systemic (if severe): Azoxystrobin 23% SC @ 1.0 ml/L or Difenoconazole 25% EC @ 0.5 ml/L.",
            "Pre-Harvest Interval (PHI): Observe 7-10 days before harvesting."
        ]
        cultural = [
            "Strictly avoid overhead sprinkler irrigation; switch to drip watering.",
            "Apply straw or plastic mulch to block soil spore splash onto foliage.",
            "Practice 3-year crop rotation with non-solanaceous crops."
        ]
        hindi = f"{crop} में अगेती झुलसा (Early Blight) रोग के लक्षण हैं। 2.5 ग्राम मैंकोजेब (Mancozeb) प्रति लीटर पानी में या नीम का तेल (5ml/लीटर) मिलाकर 10 दिन के अंतराल पर छिड़काव करें। नीचे की संक्रमित पत्तियां तोड़कर नष्ट कर दें।"
    elif "late blight" in disease.lower():
        bio = [
            "Preventive spray: Bordeaux mixture (1%) or Copper Hydroxide (2.0 g/L).",
            "Bio-control: Pseudomonas fluorescens (5 g/L) foliar spray.",
            "Immediately remove and destroy severely blighted plants to stop field contagion."
        ]
        chem = [
            "Curative systemic: Metalaxyl 8% + Mancozeb 64% WP (Ridomil MZ) @ 2.5 g/L.",
            "Alternative: Cymoxanil 8% + Mancozeb 64% WP @ 2.0 g/L or Dimethomorph 50% WP @ 1.0 g/L.",
            "Spray during dry leaf window; repeat after 7 days if overcast conditions persist."
        ]
        cultural = [
            "Plant certified blight-free seed tubers / resistant varieties.",
            "High hilling of potato ridges (20-25 cm) to protect developing tubers.",
            "Ensure wide row spacing for maximum canopy aeration."
        ]
        hindi = f"{crop} में पछेती झुलसा (Late Blight) एक गंभीर रोग है। तुरंत रिडोमिल गोल्ड (Metalaxyl + Mancozeb 2.5g/L) या साइमोक्सानिल का छिड़काव करें। खेत में पानी न रुकने दें।"
    elif "rust" in disease.lower():
        bio = [
            "Foliar spray of wettable sulfur (3 g/L) or sulfur dust.",
            "Bio-fungicide Bacillus amyloliquefaciens (2.5 g/L) spray."
        ]
        chem = [
            "Azoxystrobin 18.2% + Difenoconazole 11.4% SC @ 1.0 ml/L.",
            "Propiconazole 25% EC (Tilt) @ 1.0 ml/L at first sign of pustules."
        ]
        cultural = [
            "Plant rust-resistant hybrid varieties.",
            "Early season planting to escape late spore showers."
        ]
        hindi = f"{crop} में रतुआ/गेरुआ (Rust) रोग है। प्रोपिकोनाजोल 25% EC (1ml/लीटर) या सल्फर (3g/लीटर) का छिड़काव करें।"
    elif "bacterial spot" in disease.lower():
        bio = [
            "Copper Hydroxide (2.0 g/L) combined with Bacillus subtilis (2.5 g/L).",
            "Disinfect all cutting tools with 70% alcohol between plants."
        ]
        chem = [
            "Copper Oxychloride (2.5 g/L) + Streptocycline (0.5 g / 10 L water).",
            "Observe pre-harvest safety interval of 14 days."
        ]
        cultural = [
            "Use certified disease-free hot-water treated seeds.",
            "Do not enter or work in fields while leaves are wet with dew or rain."
        ]
        hindi = f"{crop} में जीवाणु धब्बा रोग (Bacterial Spot) है। कॉपर ऑक्सीक्लोराइड (2.5g/L) के साथ स्ट्रेप्टोसाइक्लिन (0.5g/10L) का घोल बनाकर छिड़काव करें।"
    else:
        bio = [
            "Apply Neem seed kernel extract (NSKE 5%) or cold-pressed Neem oil (5 ml/L).",
            "Spray Trichoderma or Bacillus bio-fungicide formulations."
        ]
        chem = [
            "Broad-spectrum protective: Mancozeb 75% WP @ 2.5 g/L or Copper Hydroxide @ 2.0 g/L.",
            "Follow pesticide label dosage and safety precautions."
        ]
        cultural = [
            "Improve air drainage by pruning congested stems.",
            "Destroy fallen infected crop debris."
        ]
        hindi = f"{crop} में {disease} के लक्षण हैं। नीम तेल (5ml/L) या मैंकोजेब (2.5g/L) का छिड़काव करें।"
        
    return {
        "crop": crop,
        "condition": disease,
        "is_healthy": False,
        "biological_controls": bio,
        "chemical_controls": chem,
        "cultural_prevention": cultural,
        "rag_sources": [d["source"] for d in rag_data.get("documents", [])],
        "rag_context_snippet": rag_data.get("combined_context", "")[:400],
        "hindi_summary": hindi
    }

