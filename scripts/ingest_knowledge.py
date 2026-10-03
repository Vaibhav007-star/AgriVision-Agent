"""
Knowledge Base Ingestion Script for AgriVision Agent (scripts/ingest_knowledge.py).
Parses markdown pathology documents in knowledge/documents/ and builds the FAISS vector index.
"""

import sys
from pathlib import Path

# Add project root to sys.path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from app.rag.ingest import ingest_documents

if __name__ == "__main__":
    print("[AgriVision Knowledge Ingest] Re-indexing agricultural pathology corpus...")
    stats = ingest_documents()
    print(f"[+] Successfully indexed {stats['total_chunks']} chunks into FAISS (Embedding Dim: {stats['embedding_dim']}).")
    print(f"[+] Vector store saved to: {stats['index_path']}")

