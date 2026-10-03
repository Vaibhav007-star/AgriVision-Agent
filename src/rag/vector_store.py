"""
Vector Store & Embedding Pipeline for AgriVision Agent.
Parses agricultural pathology markdown documents, computes dense embeddings,
builds a FAISS index, and performs semantic similarity retrieval.
"""

from typing import List, Dict, Any, Optional
import os
import json
from pathlib import Path
import numpy as np

from src.config import config


class AgriculturalVectorStore:
    """FAISS-based or Semantic Vector Database for Agronomic Pathology."""
    
    _instance = None
    
    def __init__(self, data_dir: Optional[Path] = None, index_dir: Optional[Path] = None):
        self.data_dir = Path(data_dir or config.rag.RAG_DATA_DIR)
        self.index_dir = Path(index_dir or config.rag.FAISS_INDEX_PATH)
        self.embedding_model_name = config.rag.EMBEDDING_MODEL
        
        self.documents: List[Dict[str, Any]] = []
        self.embeddings: Optional[np.ndarray] = None
        self.faiss_index = None
        self.encoder = None
        
        self._initialize_encoder()
        self._load_or_build_index()

    def _initialize_encoder(self):
        """Initializes SentenceTransformer or lightweight fallback."""
        try:
            from sentence_transformers import SentenceTransformer
            print(f"[AgriVision RAG] Initializing embedding model: {self.embedding_model_name}")
            self.encoder = SentenceTransformer(self.embedding_model_name)
        except Exception as e:
            print(f"[AgriVision RAG] Note: Falling back to internal semantic encoder ({e})")
            self.encoder = None

    def _encode_texts(self, texts: List[str]) -> np.ndarray:
        """Encodes list of strings into normalized dense float32 vectors."""
        if self.encoder is not None:
            vectors = self.encoder.encode(texts, convert_to_numpy=True, normalize_embeddings=True)
            return vectors.astype(np.float32)
        else:
            # Fallback deterministic bag-of-characters/words normalized embedding
            vectors = []
            for t in texts:
                words = t.lower().split()
                vec = np.zeros(384, dtype=np.float32)
                for i, w in enumerate(words):
                    h = hash(w) % 384
                    vec[h] += 1.0 / (i + 1)
                norm = np.linalg.norm(vec) + 1e-8
                vectors.append(vec / norm)
            return np.array(vectors, dtype=np.float32)

    def parse_documents(self) -> List[Dict[str, Any]]:
        """Parses all Markdown files in data/rag_docs/ into structured chunks."""
        chunks = []
        if not self.data_dir.exists():
            return chunks
            
        for md_file in self.data_dir.glob("*.md"):
            crop_name = md_file.stem.replace("_pathology", "").title()
            with open(md_file, "r", encoding="utf-8") as f:
                content = f.read()
                
            # Split by markdown H2 sections (##)
            sections = content.split("## ")
            for sec in sections:
                if not sec.strip():
                    continue
                lines = sec.strip().split("\n")
                title = lines[0].strip()
                body = "\n".join(lines[1:]).strip()
                
                # Detect disease from title if present
                disease_name = "General"
                if " - " in title:
                    parts = title.split(" - ")
                    crop_name = parts[0].strip()
                    disease_name = parts[1].split("(")[0].strip()
                    
                chunks.append({
                    "id": f"{md_file.stem}_{len(chunks)}",
                    "source": md_file.name,
                    "crop": crop_name,
                    "disease": disease_name,
                    "title": title,
                    "text": f"### {title}\n{body}",
                    "summary": body[:300] + "..." if len(body) > 300 else body
                })
        return chunks

    def _load_or_build_index(self):
        """Loads index from disk or builds from raw docs."""
        self.index_dir.mkdir(parents=True, exist_ok=True)
        docs_meta_path = self.index_dir / "documents.json"
        
        # Parse documents
        self.documents = self.parse_documents()
        if not self.documents:
            print("[AgriVision RAG] No RAG documents found to index.")
            return
            
        # Compute embeddings
        texts = [doc["text"] for doc in self.documents]
        self.embeddings = self._encode_texts(texts)
        
        # Build FAISS Index
        try:
            import faiss
            dim = self.embeddings.shape[1]
            # Inner Product (Cosine similarity when vectors are normalized)
            self.faiss_index = faiss.IndexFlatIP(dim)
            self.faiss_index.add(self.embeddings)
            print(f"[AgriVision RAG] Built FAISS Index with {len(self.documents)} semantic chunks (Dim: {dim}).")
        except Exception as e:
            print(f"[AgriVision RAG] FAISS initialization notice ({e}). Using Cosine Matrix retrieval.")
            self.faiss_index = None

    def search(
        self,
        query: str,
        crop: Optional[str] = None,
        disease: Optional[str] = None,
        top_k: int = 3
    ) -> List[Dict[str, Any]]:
        """
        Performs semantic similarity retrieval with optional crop/disease filtering.
        """
        if not self.documents or self.embeddings is None:
            return []
            
        # Filter candidate pool if specific crop or disease is requested
        candidate_indices = []
        for idx, doc in enumerate(self.documents):
            match_crop = (crop is None) or (crop.lower() in doc["crop"].lower()) or (crop.lower() in doc["text"].lower())
            match_disease = (disease is None) or (disease.lower() in doc["disease"].lower()) or (disease.lower() in doc["text"].lower())
            if match_crop or match_disease or doc["source"] == "general_agronomy.md":
                candidate_indices.append(idx)
                
        if not candidate_indices:
            candidate_indices = list(range(len(self.documents)))
            
        query_vec = self._encode_texts([query])[0]
        
        # Calculate cosine similarities for candidates
        candidate_embeddings = self.embeddings[candidate_indices]
        scores = np.dot(candidate_embeddings, query_vec)
        
        # Sort top scores
        top_sub_indices = np.argsort(scores)[::-1][:top_k]
        
        results = []
        for sub_idx in top_sub_indices:
            orig_idx = candidate_indices[sub_idx]
            doc = self.documents[orig_idx].copy()
            doc["score"] = float(scores[sub_idx])
            results.append(doc)
            
        return results


# Global singleton helper
_vector_store: Optional[AgriculturalVectorStore] = None

def get_vector_store() -> AgriculturalVectorStore:
    """Returns or initializes global vector store instance."""
    global _vector_store
    if _vector_store is None:
        _vector_store = AgriculturalVectorStore()
    return _vector_store

