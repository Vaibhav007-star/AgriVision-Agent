"""
LangGraph Multi-Node State Machine for AgriVision Agent.
Coordinates autonomous reasoning, confidence gating, RAG retrieval,
weather analysis, dosage calculations, and multi-lingual prescription synthesis.
"""

from typing import Dict, Any, List, Literal, Callable, Optional

try:
    from langgraph.graph import StateGraph as LGStateGraph, END as LG_END
    HAS_LANGGRAPH = True
except Exception:
    HAS_LANGGRAPH = False
    LGStateGraph = None
    LG_END = None

END = "__END__"


class PurePythonStateGraph:
    """Pure-Python state graph engine matching LangGraph's API."""
    def __init__(self, state_schema=None):
        self.nodes: Dict[str, Callable] = {}
        self.edges: Dict[str, str] = {}
        self.conditional_edges: Dict[str, tuple[Callable, Dict[str, str]]] = {}
        self.entry_point: Optional[str] = None

    def add_node(self, name: str, func: Callable):
        self.nodes[name] = func

    def set_entry_point(self, name: str):
        self.entry_point = name

    def add_edge(self, source: str, target: str):
        self.edges[source] = target

    def add_conditional_edges(self, source: str, routing_func: Callable, routes_map: Dict[str, str]):
        self.conditional_edges[source] = (routing_func, routes_map)

    def compile(self):
        return self

    def invoke(self, initial_state: Dict[str, Any]) -> Dict[str, Any]:
        current_state = dict(initial_state)
        current_node_name = self.entry_point

        while current_node_name and current_node_name != END and current_node_name != LG_END:
            node_fn = self.nodes.get(current_node_name)
            if not node_fn:
                break
            
            node_update = node_fn(current_state)
            if isinstance(node_update, dict):
                current_state.update(node_update)

            if current_node_name in self.conditional_edges:
                routing_func, routes_map = self.conditional_edges[current_node_name]
                route_key = routing_func(current_state)
                current_node_name = routes_map.get(route_key, END)
            elif current_node_name in self.edges:
                current_node_name = self.edges[current_node_name]
            else:
                current_node_name = END

        return current_state

from src.agent.state import AgriVisionState
from src.agent.llm_factory import get_llm
from src.rag.knowledge_base import query_rag, get_structured_prescriptions
from src.tools.weather_tool import get_weather_data
from src.tools.agri_tools import calculate_field_dosage


# --- GRAPH NODES ---

def validate_confidence_node(state: AgriVisionState) -> Dict[str, Any]:
    """Node 1: Validates model confidence against safety threshold."""
    conf = state.get("confidence", 0.0)
    thresh = state.get("confidence_threshold", 0.60)
    is_conf = conf >= thresh
    
    step_log = f"Confidence Gate: Model prediction confidence is {conf*100:.1f}% (Threshold: {thresh*100:.1f}%). Validated: {'Passed' if is_conf else 'Failed'}."
    
    return {
        "is_confident": is_conf,
        "reasoning_steps": state.get("reasoning_steps", []) + [step_log],
        "status": "in_progress" if is_conf else "requires_clarification"
    }


def handle_clarification_node(state: AgriVisionState) -> Dict[str, Any]:
    """Node 2 (Fallback): Formulates clarification request if image is ambiguous."""
    crop = state.get("crop", "Crop")
    disease = state.get("disease", "Condition")
    lang = state.get("language", "en")
    
    if lang == "hi":
        msg = f"छवि अस्पष्ट है (विश्वास स्तर केवल {state.get('confidence', 0)*100:.1f}%)। कृपया अच्छी रोशनी में पत्ती की एक स्पष्ट और नज़दीकी तस्वीर दोबारा अपलोड करें।"
    else:
        msg = f"Leaf diagnosis confidence is low ({state.get('confidence', 0)*100:.1f}%). Please upload a clearer, well-lit close-up of the infected foliage for an accurate prescription."
        
    prescription = {
        "crop": crop,
        "condition": "Ambiguous Diagnosis",
        "is_healthy": False,
        "biological_controls": ["Take a clearer photograph under natural daylight."],
        "chemical_controls": ["Do not apply chemicals before positive pathogen identification."],
        "cultural_prevention": ["Inspect both upper and lower leaf surfaces."],
        "hindi_summary": msg,
        "advisory_text": msg
    }
    
    step_log = "Clarification Node: Gated execution due to low confidence. Prompted user for re-capture."
    
    return {
        "final_prescription": prescription,
        "reasoning_steps": state.get("reasoning_steps", []) + [step_log],
        "status": "completed"
    }


def retrieve_knowledge_node(state: AgriVisionState) -> Dict[str, Any]:
    """Node 3: Performs FAISS vector search across pathology handbooks."""
    crop = state.get("crop", "Tomato")
    disease = state.get("disease", "Early Blight")
    
    query = f"{crop} {disease} pathology treatment biological control fungicide dosage"
    rag_result = query_rag(query, crop=crop, disease=disease, top_k=2)
    
    sources = [doc["source"] for doc in rag_result.get("documents", [])]
    context = rag_result.get("combined_context", "")
    
    step_log = f"RAG Retrieval: Retrieved {len(sources)} pathology document chunks ({', '.join(sources)})."
    
    return {
        "rag_context": context,
        "rag_sources": sources,
        "reasoning_steps": state.get("reasoning_steps", []) + [step_log]
    }


def analyze_weather_node(state: AgriVisionState) -> Dict[str, Any]:
    """Node 4: Evaluates ambient temperature, humidity, and spore germination risk."""
    location = state.get("location", "New Delhi, India")
    weather = get_weather_data(location)
    
    step_log = f"Weather Tool: {weather['location']} (Temp: {weather['temperature_c']}°C, Humidity: {weather['humidity_pct']}%, Spore Risk: {weather['spore_germination_risk']})."
    
    return {
        "weather_data": weather,
        "reasoning_steps": state.get("reasoning_steps", []) + [step_log]
    }


def calculate_dosage_node(state: AgriVisionState) -> Dict[str, Any]:
    """Node 5: Calculates tank spray volume and chemical/organic requirements for field acreage."""
    crop = state.get("crop", "Tomato")
    disease = state.get("disease", "Early Blight")
    acres = state.get("field_acres", 1.0)
    
    dosage = calculate_field_dosage(crop, disease, area_acres=acres)
    step_log = f"Dosage Calculation Tool: Computed tank requirements for {acres} acre(s) ({dosage['water_volume_liters']} L water, {dosage['sprayer_tanks_15L']} tanks)."
    
    return {
        "dosage_plan": dosage,
        "reasoning_steps": state.get("reasoning_steps", []) + [step_log]
    }


def synthesize_prescription_node(state: AgriVisionState) -> Dict[str, Any]:
    """Node 6: Synthesizes structured final prescription via LLM / Agronomy Engine."""
    crop = state.get("crop", "Tomato")
    disease = state.get("disease", "Early Blight")
    lang = state.get("language", "en")
    weather = state.get("weather_data", {})
    dosage = state.get("dosage_plan", {})
    
    # Generate structured baseline prescription
    structured_rx = get_structured_prescriptions(
        crop=crop,
        disease=disease,
        weather_risk=weather.get("spore_germination_risk", "Moderate"),
        language=lang
    )
    
    # Merge dosage and weather context into prescription
    structured_rx["field_dosage"] = dosage
    structured_rx["weather_alert"] = weather.get("agronomic_advice", "")
    structured_rx["spray_timing"] = weather.get("spray_recommendation", "")
    
    # Synthesize via LLM
    try:
        llm = get_llm()
        system_prompt = (
            "You are AgriVision, an autonomous agricultural doctor and agronomist. "
            "Synthesize a concise, highly practical action plan for the farmer based on the provided context."
        )
        user_prompt = (
            f"Crop: {crop}\nDisease: {disease}\nConfidence: {state.get('confidence', 0.9)*100:.1f}%\n"
            f"Weather Risk: {weather.get('spore_germination_risk', 'Moderate')}\n"
            f"Acreage: {state.get('field_acres', 1.0)} acre(s)\n"
            f"Language: {'Hindi' if lang == 'hi' else 'English'}\n\n"
            f"Context: {state.get('rag_context', '')[:500]}"
        )
        response = llm.invoke([SystemMessage(content=system_prompt), HumanMessage(content=user_prompt)])
        structured_rx["agent_explanation"] = response.content
    except Exception as e:
        structured_rx["agent_explanation"] = f"Action plan formulated based on verified agronomic standards. ({e})"
        
    step_log = f"Agent Synthesis: Completed personalized prescription formulation (Language: {lang.upper()})."
    
    return {
        "final_prescription": structured_rx,
        "reasoning_steps": state.get("reasoning_steps", []) + [step_log],
        "status": "completed"
    }


# --- CONDITIONAL ROUTING ---

def route_after_validation(state: AgriVisionState) -> Literal["retrieve_knowledge", "handle_clarification"]:
    """Conditional Edge router based on confidence validation."""
    if state.get("is_confident", True):
        return "retrieve_knowledge"
    return "handle_clarification"


# --- GRAPH BUILDER ---

def build_agrivision_agent() -> Any:
    """Builds and compiles the StateGraph workflow."""
    GraphClass = LGStateGraph if HAS_LANGGRAPH else PurePythonStateGraph
    end_symbol = LG_END if HAS_LANGGRAPH else END
    workflow = GraphClass(AgriVisionState)
    
    # Register Nodes
    workflow.add_node("validate_confidence", validate_confidence_node)
    workflow.add_node("handle_clarification", handle_clarification_node)
    workflow.add_node("retrieve_knowledge", retrieve_knowledge_node)
    workflow.add_node("analyze_weather", analyze_weather_node)
    workflow.add_node("calculate_dosage", calculate_dosage_node)
    workflow.add_node("synthesize_prescription", synthesize_prescription_node)
    
    # Set Entry Point
    workflow.set_entry_point("validate_confidence")
    
    # Add Conditional Edge from validation
    workflow.add_conditional_edges(
        "validate_confidence",
        route_after_validation,
        {
            "retrieve_knowledge": "retrieve_knowledge",
            "handle_clarification": "handle_clarification"
        }
    )
    
    # Sequential Pipeline Edges
    workflow.add_edge("retrieve_knowledge", "analyze_weather")
    workflow.add_edge("analyze_weather", "calculate_dosage")
    workflow.add_edge("calculate_dosage", "synthesize_prescription")
    workflow.add_edge("synthesize_prescription", end_symbol)
    workflow.add_edge("handle_clarification", end_symbol)
    
    return workflow.compile()


# Global agent runner instance
_agent_app = None

def run_agent_workflow(
    crop: str,
    disease: str,
    confidence: float = 0.95,
    field_acres: float = 1.0,
    location: str = "New Delhi, India",
    language: str = "en"
) -> Dict[str, Any]:
    """
    Executes the full end-to-end LangGraph agentic reasoning workflow.
    """
    global _agent_app
    if _agent_app is None:
        _agent_app = build_agrivision_agent()
        
    initial_state: AgriVisionState = {
        "crop": crop,
        "disease": disease,
        "confidence": confidence,
        "confidence_threshold": 0.60,
        "is_healthy": "healthy" in disease.lower(),
        "is_confident": False,
        "field_acres": field_acres,
        "location": location,
        "language": language,
        "rag_context": "",
        "rag_sources": [],
        "weather_data": {},
        "dosage_plan": {},
        "final_prescription": {},
        "reasoning_steps": [],
        "status": "in_progress"
    }
    
    result = _agent_app.invoke(initial_state)
    return result

