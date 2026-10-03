"""
Database management module for AgriVision Agent.
Handles SQLite storage for scans, diagnoses, chats, and telemetry.
"""

import sqlite3
import json
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any, Optional
from src.config import config

DB_PATH = Path(config.base_dir) / "data" / "agrivision.db"


def get_connection() -> sqlite3.Connection:
    """Create and return a database connection with row factory enabled."""
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    return conn


def init_db() -> None:
    """Initialize database tables if they do not exist."""
    with get_connection() as conn:
        cursor = conn.cursor()
        
        # Scans / Predictions table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS scans (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                image_path TEXT,
                crop_name TEXT NOT NULL,
                condition TEXT NOT NULL,
                is_healthy INTEGER NOT NULL,
                confidence REAL NOT NULL,
                top3_predictions TEXT, -- JSON string
                ai_diagnosis TEXT,
                treatment TEXT,
                prevention TEXT,
                weather_context TEXT,
                language TEXT DEFAULT 'en'
            )
        """)
        
        # Chat messages table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS chat_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id TEXT NOT NULL,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                role TEXT NOT NULL, -- 'user' or 'agent'
                content TEXT NOT NULL,
                language TEXT DEFAULT 'en',
                metadata TEXT -- JSON string
            )
        """)
        
        conn.commit()


def save_scan(
    crop_name: str,
    condition: str,
    is_healthy: bool,
    confidence: float,
    image_path: Optional[str] = None,
    top3_predictions: Optional[List[Dict[str, Any]]] = None,
    ai_diagnosis: Optional[str] = None,
    treatment: Optional[str] = None,
    prevention: Optional[str] = None,
    weather_context: Optional[str] = None,
    language: str = "en"
) -> int:
    """Save a disease scan record to the database."""
    init_db()
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO scans (
                crop_name, condition, is_healthy, confidence, image_path,
                top3_predictions, ai_diagnosis, treatment, prevention,
                weather_context, language
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            crop_name,
            condition,
            1 if is_healthy else 0,
            confidence,
            image_path,
            json.dumps(top3_predictions) if top3_predictions else None,
            ai_diagnosis,
            treatment,
            prevention,
            weather_context,
            language
        ))
        conn.commit()
        return cursor.lastrowid


def get_recent_scans(limit: int = 10) -> List[Dict[str, Any]]:
    """Retrieve recent scans ordered by timestamp descending."""
    init_db()
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT * FROM scans ORDER BY timestamp DESC LIMIT ?
        """, (limit,))
        rows = cursor.fetchall()
        return [dict(row) for row in rows]


def get_scan_statistics() -> Dict[str, Any]:
    """Calculate aggregate statistics for the dashboard."""
    init_db()
    with get_connection() as conn:
        cursor = conn.cursor()
        
        cursor.execute("SELECT COUNT(*) FROM scans")
        total_scans = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM scans WHERE is_healthy = 1")
        healthy_count = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM scans WHERE is_healthy = 0")
        diseased_count = cursor.fetchone()[0]
        
        cursor.execute("SELECT AVG(confidence) FROM scans")
        avg_conf_row = cursor.fetchone()[0]
        avg_confidence = float(avg_conf_row) if avg_conf_row is not None else 0.0
        
        cursor.execute("""
            SELECT condition, COUNT(*) as count 
            FROM scans 
            WHERE is_healthy = 0 
            GROUP BY condition 
            ORDER BY count DESC 
            LIMIT 5
        """)
        top_diseases = [dict(row) for row in cursor.fetchall()]
        
        return {
            "total_scans": total_scans,
            "healthy_count": healthy_count,
            "diseased_count": diseased_count,
            "avg_confidence": round(avg_confidence * 100, 2),
            "top_diseases": top_diseases
        }


def save_chat_message(session_id: str, role: str, content: str, language: str = "en", metadata: Optional[Dict[str, Any]] = None) -> int:
    """Saves a conversation turn to SQLite."""
    init_db()
    with get_connection() as conn:
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


def get_chat_history(session_id: str = "default_session", limit: int = 50) -> List[Dict[str, Any]]:
    """Retrieves conversation history for a session."""
    init_db()
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT * FROM chat_history WHERE session_id = ? ORDER BY timestamp ASC LIMIT ?
        """, (session_id, limit))
        return [dict(row) for row in cursor.fetchall()]


