"""
Knowledge Retrieval Node (app/agent/nodes/knowledge_retrieval.py).
Queries the FAISS vector store for grounded agricultural pathology evidence.
"""

from typing import Dict, Any
from app.agent.state import AgentState
from app.rag.retriever import retrieve_pathology_context


def knowledge_retrieval_node(state: AgentState) -> Dict[str, Any]:
    """Retrieves dense pathology chunks from FAISS."""
    steps = state.get("reasoning_steps", []).copy()
    crop = state.get("crop", "Tomato")
    disease = state.get("disease", "Early Blight")
    
    rag_context = retrieve_pathology_context(crop, disease)
    sources = rag_context.get("sources", [])
    
    steps.append(f"📚 [Knowledge Retrieval Node] Retrieved {len(sources)} grounded pathology manuals from FAISS vector store: {', '.join(sources) if sources else 'General Agronomy'}.")
    
    return {
        "retrieved_documents": rag_context.get("sources", []),
        "treatment": rag_context.get("chemical_controls", []),
        "prevention": rag_context.get("cultural_prevention", []),
        "reasoning_steps": steps
    }

