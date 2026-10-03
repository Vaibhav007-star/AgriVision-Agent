"""
Unit tests for RAG Pipeline, Ingestion, and FAISS Vector Store (tests/test_rag.py).
"""

import unittest
from pathlib import Path
from app.rag.vectorstore import get_vector_store
from app.rag.retriever import retrieve_pathology_context


class TestRAG(unittest.TestCase):
    
    def test_vectorstore_query(self):
        vs = get_vector_store()
        results = vs.similarity_search("Tomato Early Blight", top_k=2)
        self.assertGreaterEqual(len(results), 1)
        self.assertIn("text", results[0])
        
    def test_retriever_grounding(self):
        ctx = retrieve_pathology_context("Tomato", "Early Blight")
        self.assertTrue(ctx["is_verified"])
        self.assertGreater(len(ctx["biological_controls"]), 0)
        self.assertGreater(len(ctx["chemical_controls"]), 0)
        
    def test_retriever_safety_fallback(self):
        ctx = retrieve_pathology_context("UnknownCrop", "UnknownPathogen_999", min_confidence=0.99)
        self.assertFalse(ctx["is_verified"])
        self.assertIn("safety_warning", ctx)


if __name__ == "__main__":
    unittest.main()

