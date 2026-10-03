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

