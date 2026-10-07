"""
FAISS Vector Store Interface for AgriVision Agent (app/rag/vectorstore.py).
Provides fast, in-memory dense cosine similarity search over agricultural pathology chunks.
"""

from typing import List, Dict, Any, Optional
from pathlib import Path
import json
import numpy as np
try:
    import faiss
except (ImportError, Exception):
    faiss = None

try:
    from sentence_transformers import SentenceTransformer
except Exception:
    SentenceTransformer = None

BASE_DIR = Path(__file__).resolve().parent.parent.parent
EMBEDDING_MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"
DEFAULT_INDEX_DIR = BASE_DIR / "knowledge" / "vectorstore"


class FAISSVectorStore:
    """Singleton-style FAISS / Semantic Vector Store Manager."""
    
    _instance = None
    
    def __init__(self, index_dir: Optional[Path] = None):
        if index_dir is None:
            index_dir = DEFAULT_INDEX_DIR
        self.index_dir = Path(index_dir)
        self.index_file = self.index_dir / "index.faiss"
        self.metadata_file = self.index_dir / "metadata.json"
        self.embeddings_file = self.index_dir / "embeddings.npy"
        
        self.index = None
        self.embeddings: Optional[np.ndarray] = None
        self.metadata: List[Dict[str, Any]] = []
        self.embedding_model: Optional[SentenceTransformer] = None
        
        self._load_or_build()
        
    def _load_or_build(self):
        """Loads FAISS index or embedding vectors from disk, or triggers ingestion."""
        if not self.index_file.exists() or not self.metadata_file.exists():
            # Check fallback directory in data/processed/faiss_index
            fallback_index = BASE_DIR / "data" / "processed" / "faiss_index" / "index.faiss"
            fallback_meta = BASE_DIR / "data" / "processed" / "faiss_index" / "metadata.json"
            if fallback_index.exists() and fallback_meta.exists():
                self.index_file = fallback_index
                self.metadata_file = fallback_meta
            else:
                from app.rag.ingest import ingest_documents
                ingest_documents(vectorstore_dir=self.index_dir)
                
        # Read index if faiss is available
        if faiss is not None and self.index_file.exists():
            try:
                self.index = faiss.read_index(str(self.index_file))
            except Exception:
                self.index = None
                
        # Read metadata
        if self.metadata_file.exists():
            with open(self.metadata_file, "r", encoding="utf-8") as f:
                self.metadata = json.load(f)
                
        # Read pre-computed embeddings if present
        if self.embeddings_file.exists():
            try:
                self.embeddings = np.load(self.embeddings_file)
            except Exception:
                self.embeddings = None
            
        if SentenceTransformer is not None:
            try:
                self.embedding_model = SentenceTransformer(EMBEDDING_MODEL_NAME)
            except Exception:
                self.embedding_model = None
        else:
            self.embedding_model = None
        
    def similarity_search(
        self,
        query: str,
        top_k: int = 3,
        score_threshold: float = 0.35,
        crop_filter: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Computes cosine similarity search over vector store chunks.
        """
        if (self.index is None and self.embeddings is None and not self.metadata):
            self._load_or_build()
            
        if self.embedding_model is not None:
            query_vec = self.embedding_model.encode([query], normalize_embeddings=True)
            query_vec = np.array(query_vec, dtype=np.float32)
            
            if self.index is not None:
                raw_scores, raw_indices = self.index.search(query_vec, min(top_k * 3, self.index.ntotal))
                scores = raw_scores[0]
                indices = raw_indices[0]
            else:
                if self.embeddings is None and self.metadata:
                    texts = [c.get("clean_text", c.get("text", "")) for c in self.metadata]
                    self.embeddings = np.array(self.embedding_model.encode(texts, normalize_embeddings=True), dtype=np.float32)
                sims = np.dot(query_vec, self.embeddings.T)[0]
                ranked = np.argsort(sims)[::-1][:min(top_k * 3, len(sims))]
                scores = sims[ranked]
                indices = ranked
        else:
            # Lexical term frequency fallback when deep embeddings are blocked
            q_terms = [t.lower() for t in query.split() if len(t) > 2]
            scored = []
            for idx, c in enumerate(self.metadata):
                txt = (c.get("clean_text", "") + " " + c.get("crop", "") + " " + c.get("disease", "")).lower()
                matches = sum(1 for term in q_terms if term in txt)
                score = matches / (len(q_terms) or 1)
                if score > 0.0:
                    scored.append((score, idx))
            scored.sort(reverse=True, key=lambda x: x[0])
            scores = [s[0] for s in scored[:top_k * 3]]
            indices = [s[1] for s in scored[:top_k * 3]]
        
        results = []
        for score, idx in zip(scores, indices):
            if idx < 0 or idx >= len(self.metadata):
                continue
            if score < score_threshold:
                continue
                
            chunk = self.metadata[idx].copy()
            chunk["score"] = float(score)
            
            if crop_filter and crop_filter.lower() != "general":
                if chunk["crop"].lower() != "general" and crop_filter.lower() not in chunk["crop"].lower():
                    continue
                    
            results.append(chunk)
            if len(results) >= top_k:
                break
                
        return results


_GLOBAL_VECTORSTORE: Optional[FAISSVectorStore] = None

def get_vector_store(index_dir: Optional[Path] = None, force_rebuild: bool = False) -> FAISSVectorStore:
    """Returns singleton instance of FAISSVectorStore."""
    global _GLOBAL_VECTORSTORE
    if _GLOBAL_VECTORSTORE is None or force_rebuild:
        _GLOBAL_VECTORSTORE = FAISSVectorStore(index_dir=index_dir)
    return _GLOBAL_VECTORSTORE

