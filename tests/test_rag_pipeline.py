"""
Unit tests for Agricultural Knowledge Base, FAISS Vector Store, and RAG retrieval.
"""

import unittest
from pathlib import Path

from src.rag.vector_store import AgriculturalVectorStore, get_vector_store
from src.rag.knowledge_base import query_rag, get_structured_prescriptions


class TestRAGPipeline(unittest.TestCase):
    
    def setUp(self):
        self.store = get_vector_store()
        
    def test_document_parsing(self):
        docs = self.store.parse_documents()
        self.assertGreater(len(docs), 0)
        # Check metadata fields
        first = docs[0]
        self.assertIn("crop", first)
        self.assertIn("disease", first)
        self.assertIn("text", first)
        self.assertIn("source", first)
        
    def test_semantic_search(self):
        results = self.store.search("How to cure early blight in tomato?", crop="Tomato", top_k=2)
        self.assertGreater(len(results), 0)
        self.assertIn("Tomato", results[0]["text"])
        self.assertIn("score", results[0])
        
    def test_query_rag_helper(self):
        response = query_rag("Potato late blight fungicide dosage", crop="Potato", top_k=2)
        self.assertIn("documents", response)
        self.assertIn("combined_context", response)
        self.assertGreater(len(response["documents"]), 0)
        
    def test_structured_prescriptions(self):
        rx = get_structured_prescriptions("Tomato", "Early Blight", language="en")
        self.assertFalse(rx["is_healthy"])
        self.assertGreater(len(rx["biological_controls"]), 0)
        self.assertGreater(len(rx["chemical_controls"]), 0)
        self.assertGreater(len(rx["cultural_prevention"]), 0)
        self.assertIn("hindi_summary", rx)
        
    def test_healthy_prescription(self):
        rx = get_structured_prescriptions("Apple", "Healthy", language="en")
        self.assertTrue(rx["is_healthy"])


if __name__ == "__main__":
    unittest.main()

