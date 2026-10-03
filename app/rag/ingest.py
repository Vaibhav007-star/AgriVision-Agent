"""
Document Ingestion & FAISS Vector Index Construction (app/rag/ingest.py).
Parses curated agricultural pathology documents in knowledge/documents/,
generates dense 384-dimensional embeddings, and builds a serialized FAISS index.
"""

from typing import List, Dict, Any, Optional
import os
import sys
from pathlib import Path
import json
import re
import numpy as np
try:
    import faiss
except (ImportError, Exception):
    faiss = None
from sentence_transformers import SentenceTransformer

# Ensure project root is in sys.path
BASE_DIR = Path(__file__).resolve().parent.parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

EMBEDDING_MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"
DOCS_DIR = BASE_DIR / "knowledge" / "documents"
PROCESSED_DIR = BASE_DIR / "knowledge" / "processed"
VECTORSTORE_DIR = BASE_DIR / "knowledge" / "vectorstore"


def parse_markdown_document(filepath: Path) -> List[Dict[str, Any]]:
    """
    Parses a markdown document into distinct semantic chunks based on headers.
    """
    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()

    doc_title = filepath.stem.replace("_", " ").title()
    sections = re.split(r'\n(?=#{1,3}\s+)', content)
    chunks = []

    for sec in sections:
        sec = sec.strip()
        if not sec:
            continue

        header_match = re.match(r'^(#{1,3})\s+(.+)$', sec, re.MULTILINE)
        section_name = header_match.group(2).strip() if header_match else "General Info"
        
        # Clean markdown formatting for dense embedding
        clean_text = re.sub(r'#{1,6}\s+', '', sec)
        clean_text = re.sub(r'\*\*(.+?)\*\*', r'\1', clean_text)
        clean_text = re.sub(r'\[(.+?)\]\(.+?\)', r'\1', clean_text)
        clean_text = re.sub(r'\n+', ' ', clean_text).strip()

        if len(clean_text) < 40:
            continue

        # Extract target crop and disease tags
        crop_tag = "General"
        disease_tag = "Agronomy"
        
        for c in ["Tomato", "Potato", "Corn", "Apple", "Pepper", "Grape"]:
            if c.lower() in doc_title.lower() or c.lower() in clean_text.lower():
                crop_tag = c
                break
                
        for d in ["Early Blight", "Late Blight", "Common Rust", "Apple Scab", "Bacterial Spot", "Black Rot", "Healthy"]:
            if d.lower() in clean_text.lower() or d.lower() in section_name.lower():
                disease_tag = d
                break

        chunks.append({
            "chunk_id": f"{filepath.stem}_{len(chunks) + 1:03d}",
            "source": str(filepath.relative_to(BASE_DIR)).replace("\\", "/"),
            "doc_title": doc_title,
            "section": section_name,
            "crop": crop_tag,
            "disease": disease_tag,
            "text": sec,
            "clean_text": clean_text
        })

    return chunks


def ingest_documents(
    docs_dir: Optional[Path] = None,
    processed_dir: Optional[Path] = None,
    vectorstore_dir: Optional[Path] = None
) -> Dict[str, Any]:
    """
    Executes end-to-end ingestion pipeline:
    1. Parse markdown files in knowledge/documents/
    2. Save processed chunks to knowledge/processed/chunks.json
    3. Generate 384-dimensional embeddings
    4. Build and save FAISS IndexFlatIP index to knowledge/vectorstore/
    """
    if docs_dir is None:
        docs_dir = DOCS_DIR
    if processed_dir is None:
        processed_dir = PROCESSED_DIR
    if vectorstore_dir is None:
        vectorstore_dir = VECTORSTORE_DIR
        
    docs_dir.mkdir(parents=True, exist_ok=True)
    processed_dir.mkdir(parents=True, exist_ok=True)
    vectorstore_dir.mkdir(parents=True, exist_ok=True)
    
    # Fallback to data/rag_docs if knowledge/documents is empty
    md_files = list(docs_dir.glob("*.md"))
    if not md_files:
        fallback_dir = BASE_DIR / "data" / "rag_docs"
        if fallback_dir.exists():
            md_files = list(fallback_dir.glob("*.md"))
            
    if not md_files:
        raise FileNotFoundError(f"No markdown pathology documents found in {docs_dir} or {BASE_DIR / 'data' / 'rag_docs'}")
        
    all_chunks = []
    for f in md_files:
        chunks = parse_markdown_document(f)
        all_chunks.extend(chunks)
        
    print(f"[AgriVision Ingest] Parsed {len(all_chunks)} semantic chunks across {len(md_files)} documents.")
    
    # Save processed chunks
    chunks_path = processed_dir / "chunks.json"
    with open(chunks_path, "w", encoding="utf-8") as f:
        json.dump(all_chunks, f, indent=2)
        
    # Generate Embeddings
    print(f"[AgriVision Ingest] Generating embeddings via {EMBEDDING_MODEL_NAME}...")
    model = SentenceTransformer(EMBEDDING_MODEL_NAME)
    texts_to_embed = [c["clean_text"] for c in all_chunks]
    embeddings = model.encode(texts_to_embed, normalize_embeddings=True, show_progress_bar=False)
    embeddings = np.array(embeddings, dtype=np.float32)
    
    dim = embeddings.shape[1]
    
    # Always save raw embeddings.npy for universal vector search
    np.save(vectorstore_dir / "embeddings.npy", embeddings)
    
    # Save FAISS Index if available
    index_file = vectorstore_dir / "index.faiss"
    meta_file = vectorstore_dir / "metadata.json"
    
    if faiss is not None:
        try:
            index = faiss.IndexFlatIP(dim)
            index.add(embeddings)
            faiss.write_index(index, str(index_file))
            print(f"[+] Saved FAISS index ({index.ntotal} vectors, Dim: {dim}) to: {index_file}")
        except Exception:
            pass
            
    with open(meta_file, "w", encoding="utf-8") as f:
        json.dump(all_chunks, f, indent=2)
    print(f"[+] Saved chunk metadata to: {meta_file}")
    
    return {
        "total_chunks": len(all_chunks),
        "embedding_dim": dim,
        "index_path": str(index_file),
        "metadata_path": str(meta_file)
    }


if __name__ == "__main__":
    ingest_documents()

