"""
CRUD (Create, Read, Update, Delete) & Analytics Operations for AgriVision Agent SQLite Database.
"""

from typing import List, Dict, Any, Optional
import json
from app.database.database import get_db_connection, init_db


def save_prediction(
    crop: str,
    disease: str,
    confidence: float,
    crop_stage: str = "Vegetative",
    language: str = "en",
    recommendation: Optional[str] = None,
    image_path: Optional[str] = None,
    weather_context: Optional[str] = None,
    treatment: Optional[str] = None,
    prevention: Optional[str] = None,
    top3_predictions: Optional[List[Dict[str, Any]]] = None
) -> int:
    """Inserts a new crop diagnosis record into SQLite."""
    init_db()
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO predictions (
                crop, disease, confidence, crop_stage, language,
                recommendation, image_path, weather_context, treatment,
                prevention, top3_json
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            crop,
            disease,
            confidence,
            crop_stage,
            language,
            recommendation,
            image_path,
            weather_context,
            treatment,
            prevention,
            json.dumps(top3_predictions) if top3_predictions else None
        ))
        conn.commit()
        return cursor.lastrowid


def get_recent_predictions(limit: int = 25) -> List[Dict[str, Any]]:
    """Fetches most recent prediction records."""
    init_db()
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT * FROM predictions ORDER BY timestamp DESC LIMIT ?
        """, (limit,))
        return [dict(row) for row in cursor.fetchall()]


def get_prediction_stats() -> Dict[str, Any]:
    """Computes aggregate analytics over stored predictions."""
    init_db()
    with get_db_connection() as conn:
        cursor = conn.cursor()
        
        cursor.execute("SELECT COUNT(*) FROM predictions")
        total = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM predictions WHERE LOWER(disease) LIKE '%healthy%'")
        healthy_count = cursor.fetchone()[0]
        diseased_count = max(0, total - healthy_count)
        
        cursor.execute("SELECT AVG(confidence) FROM predictions")
        avg_conf_row = cursor.fetchone()[0]
        avg_conf = float(avg_conf_row) if avg_conf_row is not None else 0.94
        
        cursor.execute("""
            SELECT disease, COUNT(*) as count 
            FROM predictions 
            WHERE LOWER(disease) NOT LIKE '%healthy%'
            GROUP BY disease 
            ORDER BY count DESC 
            LIMIT 5
        """)
        top_diseases = [{"disease": row[0], "count": row[1]} for row in cursor.fetchall()]
        
        return {
            "total_scans": total,
            "healthy_count": healthy_count,
            "diseased_count": diseased_count,
            "avg_confidence": round(avg_conf * 100, 2),
            "top_diseases": top_diseases
        }


def save_chat_turn(
    session_id: str,
    role: str,
    content: str,
    language: str = "en",
    metadata: Optional[Dict[str, Any]] = None
) -> int:
    """Saves a farmer-chatbot dialogue turn."""
    init_db()
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO chat_history (session_id, role, content, language, metadata)
            VALUES (?, ?, ?, ?, ?)
        """, (
            session_id,
            role,
            content,
            language,
            json.dumps(metadata) if metadata else None
        ))
        conn.commit()
        return cursor.lastrowid


def get_chat_turns(session_id: str = "default_session", limit: int = 50) -> List[Dict[str, Any]]:
    """Retrieves conversation history for a given session."""
    init_db()
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT * FROM chat_history WHERE session_id = ? ORDER BY timestamp ASC LIMIT ?
        """, (session_id, limit))
        return [dict(row) for row in cursor.fetchall()]


# ---------------------------------------------------------------------------
# Haryana Offline Agronomy & Localized Diagnostic Records CRUD
# ---------------------------------------------------------------------------

def _deserialize_block_row(row: Any) -> Dict[str, Any]:
    """Helper to convert SQLite row with JSON fields into structured Python dict."""
    row_dict = dict(row)
    for field, key in [
        ("primary_crops_json", "primary_crops"),
        ("top_3_diseases_json", "top_3_diseases"),
        ("symptom_checklist_json", "symptom_checklist"),
        ("approved_pesticide_solution_json", "approved_pesticide_solution"),
    ]:
        raw_val = row_dict.pop(field, None)
        if raw_val:
            try:
                row_dict[key] = json.loads(raw_val)
            except Exception:
                row_dict[key] = raw_val
        else:
            row_dict[key] = [] if "list" in key or "crops" in key or "diseases" in key else {}
    return row_dict


def get_offline_agronomy_blocks(
    district: Optional[str] = None,
    dialect: Optional[str] = None,
    crop: Optional[str] = None
) -> List[Dict[str, Any]]:
    """
    Fetches offline agronomy blocks from SQLite with optional filtering
    by district, primary dialect, or primary crop.
    """
    init_db()
    query = "SELECT * FROM haryana_offline_agronomy WHERE 1=1"
    params: List[Any] = []

    if district:
        query += " AND LOWER(district) = LOWER(?)"
        params.append(district.strip())

    if dialect:
        query += " AND LOWER(primary_dialect) LIKE LOWER(?)"
        params.append(f"%{dialect.strip()}%")

    if crop:
        query += " AND LOWER(primary_crops_json) LIKE LOWER(?)"
        params.append(f"%{crop.strip()}%")

    query += " ORDER BY district ASC, block_name ASC"

    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(query, params)
        rows = cursor.fetchall()
        return [_deserialize_block_row(r) for r in rows]


def get_offline_agronomy_by_block(district: str, block_name: str) -> Optional[Dict[str, Any]]:
    """Fetches diagnostic and advisory profile for a specific administrative block."""
    init_db()
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT * FROM haryana_offline_agronomy 
            WHERE LOWER(district) = LOWER(?) AND (LOWER(block_name) = LOWER(?) OR LOWER(block_name) LIKE LOWER(?))
            LIMIT 1
        """, (district.strip(), block_name.strip(), f"%{block_name.strip()}%"))
        row = cursor.fetchone()
        return _deserialize_block_row(row) if row else None


def get_all_districts_agronomy() -> List[str]:
    """Returns a distinct sorted list of all 22 Haryana districts registered in the agronomy database."""
    init_db()
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT DISTINCT district FROM haryana_offline_agronomy ORDER BY district ASC")
        return [r[0] for r in cursor.fetchall()]


def get_all_dialects_agronomy() -> List[str]:
    """Returns a distinct sorted list of local linguistic dialects in Haryana."""
    init_db()
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT DISTINCT primary_dialect FROM haryana_offline_agronomy ORDER BY primary_dialect ASC")
        return [r[0] for r in cursor.fetchall()]


def search_offline_agronomy_by_crop(crop_query: str) -> List[Dict[str, Any]]:
    """Searches Haryana blocks where the given crop is primarily cultivated."""
    return get_offline_agronomy_blocks(crop=crop_query)

