"""
Unit and Integration tests for RAG Module in app/rag (Phase 4).
"""

import unittest
from pathlib import Path
import json

from app.rag.ingest import parse_markdown_document, ingest_documents
from app.rag.vectorstore import get_vector_store
from app.rag.retriever import retrieve_pathology_context


class TestAppRAG(unittest.TestCase):
    
    def setUp(self):
        self.base_dir = Path(__file__).resolve().parent.parent
        self.sample_doc = self.base_dir / "knowledge" / "documents" / "tomato_pathology.md"
        
    def test_markdown_chunk_parsing(self):
        if self.sample_doc.exists():
            chunks = parse_markdown_document(self.sample_doc)
            self.assertGreaterEqual(len(chunks), 1)
            first = chunks[0]
            self.assertIn("chunk_id", first)
            self.assertIn("source", first)
            self.assertIn("crop", first)
            self.assertIn("clean_text", first)
            
    def test_vectorstore_similarity_search(self):
        vs = get_vector_store()
        results = vs.similarity_search("Tomato Early Blight organic Neem spray", top_k=2)
        self.assertGreaterEqual(len(results), 1)
        self.assertIn("text", results[0])
        self.assertGreater(results[0]["score"], 0.0)
        
    def test_retriever_grounded_prescription(self):
        ctx = retrieve_pathology_context("Tomato", "Early Blight")
        self.assertTrue(ctx["is_verified"])
        self.assertEqual(ctx["crop"], "Tomato")
        self.assertGreater(len(ctx["biological_controls"]), 0)
        self.assertGreater(len(ctx["chemical_controls"]), 0)
        self.assertGreater(len(ctx["sources"]), 0)
        
    def test_retriever_safety_guard_for_unknown(self):
        ctx = retrieve_pathology_context("UnknownCrop", "UnknownDisease_XYZ", min_confidence=0.99)
        self.assertFalse(ctx["is_verified"])
        self.assertIn("safety_warning", ctx)
        self.assertIn("don't have enough verified information", ctx["safety_warning"].lower())


if __name__ == "__main__":
    unittest.main()

