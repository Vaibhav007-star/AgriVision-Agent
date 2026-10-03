"""
State Definition for AgriVision LangGraph Agent.
Maintains execution state, reasoning history, and data flow across graph nodes.
"""

from typing import TypedDict, List, Dict, Any, Optional


class AgriVisionState(TypedDict):
    """Execution state schema for the AgriVision autonomous agent."""
    
    # Input diagnosis & meta
    crop: str
    disease: str
    confidence: float
    confidence_threshold: float
    is_healthy: bool
    is_confident: bool
    field_acres: float
    location: str
    language: str # "en" or "hi"
    
    # RAG Retrieval outputs
    rag_context: str
    rag_sources: List[str]
    
    # Tool outputs
    weather_data: Dict[str, Any]
    dosage_plan: Dict[str, Any]
    
    # Agent Reasoning & Prescriptions
    reasoning_steps: List[str]
    final_prescription: Dict[str, Any]
    status: str # "completed", "requires_clarification", "in_progress"

