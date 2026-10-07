"""
Typed State Schema for AgriVision LangGraph Multi-Node Workflow (app/agent/state.py).
"""

from typing import TypedDict, List, Dict, Any, Optional


class AgentState(TypedDict):
    """
    Defines the typed multi-turn state carried across LangGraph reasoning nodes.
    """
    # Visual & Identification Inputs
    image_path: Optional[str]
    is_leaf: Optional[bool]
    leaf_validation: Optional[Dict[str, Any]]
    crop: str
    disease: str
    confidence: float
    confidence_level: str
    is_confident: bool
    crop_stage: str
    
    # Contextual Parameters
    location: str
    field_acres: float
    language: str
    user_question: Optional[str]
    
    # Tool Execution Results
    weather: Dict[str, Any]
    retrieved_documents: List[Dict[str, Any]]
    dosage_plan: Dict[str, Any]
    crop_info: Dict[str, Any]
    disease_info: Dict[str, Any]
    
    # Prescriptive Action Plans
    treatment: List[str]
    prevention: List[str]
    final_response: str
    final_prescription: Dict[str, Any]
    
    # Execution Trace
    reasoning_steps: List[str]
    clarification_needed: bool

