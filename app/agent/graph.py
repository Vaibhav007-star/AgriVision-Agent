"""
LangGraph Multi-Node State Machine Architecture (app/agent/graph.py).
Orchestrates: Image Analysis -> Diagnosis / Confidence Check -> Weather Analysis -> RAG Retrieval -> Recommendation -> Response.
Includes a self-contained pure-Python StateGraph execution engine to guarantee 100% offline, zero-DLL dependency execution.
"""

from typing import Dict, Any, Optional, Callable, List

from app.agent.state import AgentState
from app.agent.nodes.image_analysis import image_analysis_node
from app.agent.nodes.diagnosis import diagnosis_node
from app.agent.nodes.weather import weather_node
from app.agent.nodes.knowledge_retrieval import knowledge_retrieval_node
from app.agent.nodes.recommendation import recommendation_node
from app.agent.nodes.response import response_node

END = "__END__"


class PurePythonStateGraph:
    """
    Pure-Python StateGraph engine matching LangGraph's API.
    Guarantees 100% zero-DLL reliability on Windows student laptops without AppLocker issues.
    """
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

    def invoke(self, initial_state: AgentState) -> AgentState:
        current_state = dict(initial_state)
        current_node_name = self.entry_point

        while current_node_name and current_node_name != END:
            node_fn = self.nodes.get(current_node_name)
            if not node_fn:
                break
            
            # Execute node
            node_update = node_fn(current_state)
            if isinstance(node_update, dict):
                current_state.update(node_update)

            # Determine next node
            if current_node_name in self.conditional_edges:
                routing_func, routes_map = self.conditional_edges[current_node_name]
                route_key = routing_func(current_state)
                current_node_name = routes_map.get(route_key, END)
            elif current_node_name in self.edges:
                current_node_name = self.edges[current_node_name]
            else:
                current_node_name = END

        return current_state


def route_after_diagnosis(state: AgentState) -> str:
    """Conditional router after confidence validation."""
    if state.get("is_confident", True):
        return "weather"
    else:
        return "response"


def build_agrivision_agent_graph() -> Any:
    """Constructs and compiles the StateGraph workflow."""
    # Attempt to load langgraph if DLLs permit, else use pure Python state graph
    try:
        from langgraph.graph import StateGraph as LGStateGraph, END as LG_END
        workflow = LGStateGraph(AgentState)
        workflow.add_node("image_analysis", image_analysis_node)
        workflow.add_node("diagnosis", diagnosis_node)
        workflow.add_node("weather", weather_node)
        workflow.add_node("knowledge_retrieval", knowledge_retrieval_node)
        workflow.add_node("recommendation", recommendation_node)
        workflow.add_node("response", response_node)
        workflow.set_entry_point("image_analysis")
        workflow.add_edge("image_analysis", "diagnosis")
        workflow.add_conditional_edges("diagnosis", route_after_diagnosis, {"weather": "weather", "response": "response"})
        workflow.add_edge("weather", "knowledge_retrieval")
        workflow.add_edge("knowledge_retrieval", "recommendation")
        workflow.add_edge("recommendation", "response")
        workflow.add_edge("response", LG_END)
        return workflow.compile()
    except Exception:
        # Pure Python robust fallback
        workflow = PurePythonStateGraph(AgentState)
        workflow.add_node("image_analysis", image_analysis_node)
        workflow.add_node("diagnosis", diagnosis_node)
        workflow.add_node("weather", weather_node)
        workflow.add_node("knowledge_retrieval", knowledge_retrieval_node)
        workflow.add_node("recommendation", recommendation_node)
        workflow.add_node("response", response_node)
        workflow.set_entry_point("image_analysis")
        workflow.add_edge("image_analysis", "diagnosis")
        workflow.add_conditional_edges("diagnosis", route_after_diagnosis, {"weather": "weather", "response": "response"})
        workflow.add_edge("weather", "knowledge_retrieval")
        workflow.add_edge("knowledge_retrieval", "recommendation")
        workflow.add_edge("recommendation", "response")
        workflow.add_edge("response", END)
        return workflow.compile()


# Global compiled workflow instance
_COMPILED_AGENT_GRAPH = None

def run_agent_workflow(
    crop: str,
    disease: str,
    confidence: float,
    field_acres: float = 1.0,
    location: str = "Bhopal, India",
    crop_stage: str = "Vegetative Growth",
    language: str = "en",
    user_question: Optional[str] = None,
    image_path: Optional[str] = None
) -> Dict[str, Any]:
    """
    Executes the compiled multi-node LangGraph state machine.
    """
    global _COMPILED_AGENT_GRAPH
    if _COMPILED_AGENT_GRAPH is None:
        _COMPILED_AGENT_GRAPH = build_agrivision_agent_graph()
        
    initial_state: AgentState = {
        "image_path": image_path,
        "crop": crop,
        "disease": disease,
        "confidence": confidence,
        "confidence_level": "High" if confidence >= 0.80 else ("Moderate" if confidence >= 0.60 else "Low"),
        "is_confident": confidence >= 0.60,
        "crop_stage": crop_stage,
        "location": location,
        "field_acres": field_acres,
        "language": language,
        "user_question": user_question,
        "weather": {},
        "retrieved_documents": [],
        "dosage_plan": {},
        "crop_info": {},
        "disease_info": {},
        "treatment": [],
        "prevention": [],
        "final_response": "",
        "final_prescription": {},
        "reasoning_steps": [],
        "clarification_needed": False
    }
    
    result = _COMPILED_AGENT_GRAPH.invoke(initial_state)
    return result


if __name__ == "__main__":
    res = run_agent_workflow("Tomato", "Early Blight", 0.94, field_acres=2.0)
    print("Execution Steps:")
    for s in res["reasoning_steps"]:
        print(" ->", s)
    print("\nFinal Response:")
    print(res["final_response"])
