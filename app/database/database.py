"""
SQLite Database Connection and Initialization Engine for AgriVision Agent.
Provides lightweight, reliable local SQLite persistence without requiring external database servers.
"""

from pathlib import Path
import sqlite3
import os

# Default SQLite database path
BASE_DIR = Path(__file__).resolve().parent.parent.parent
DB_PATH = BASE_DIR / "data" / "agrivision.db"


def get_db_connection(db_path: Path = DB_PATH) -> sqlite3.Connection:
    """Returns a thread-safe SQLite connection with row factory enabled."""
    db_path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(db_path), timeout=15.0, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn


def init_db(db_path: Path = DB_PATH) -> None:
    """Initializes the required SQLite database tables if they do not exist."""
    with get_db_connection(db_path) as conn:
        cursor = conn.cursor()
        
        # 1. Predictions Table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS predictions (
                prediction_id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                crop TEXT NOT NULL,
                disease TEXT NOT NULL,
                confidence REAL NOT NULL,
                crop_stage TEXT DEFAULT 'Vegetative',
                language TEXT DEFAULT 'en',
                recommendation TEXT,
                image_path TEXT,
                weather_context TEXT,
                treatment TEXT,
                prevention TEXT,
                top3_json TEXT
            )
        """)
        
        # 2. Chat History Table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS chat_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id TEXT NOT NULL,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                role TEXT NOT NULL,
                content TEXT NOT NULL,
                language TEXT DEFAULT 'en',
                metadata TEXT
            )
        """)
        
        # 3. Haryana Block-Wise Offline Agronomy & Localized Solutions Table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS haryana_offline_agronomy (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                district TEXT NOT NULL,
                block_name TEXT NOT NULL,
                primary_dialect TEXT NOT NULL,
                primary_crops_json TEXT NOT NULL,
                top_3_diseases_json TEXT NOT NULL,
                symptom_checklist_json TEXT NOT NULL,
                approved_pesticide_solution_json TEXT NOT NULL,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(district, block_name)
            )
        """)
        
        conn.commit()

    # Seed Haryana block agronomy if needed
    seed_haryana_offline_agronomy(db_path=db_path)


def seed_haryana_offline_agronomy(db_path: Path = DB_PATH) -> int:
    """
    Seeds Haryana block agronomy records into the local SQLite database.
    Uses INSERT OR REPLACE to keep regional agronomy recommendations up-to-date.
    """
    import json
    try:
        from src.data.haryana_block_agronomy import HARYANA_BLOCK_AGRONOMY
    except ImportError:
        try:
            from app.data.haryana_block_agronomy import HARYANA_BLOCK_AGRONOMY
        except ImportError:
            return 0

    inserted_count = 0
    with get_db_connection(db_path) as conn:
        cursor = conn.cursor()
        for item in HARYANA_BLOCK_AGRONOMY:
            cursor.execute("""
                INSERT OR REPLACE INTO haryana_offline_agronomy (
                    district,
                    block_name,
                    primary_dialect,
                    primary_crops_json,
                    top_3_diseases_json,
                    symptom_checklist_json,
                    approved_pesticide_solution_json
                ) VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                item.get("District_Name", ""),
                item.get("Block_Name", ""),
                item.get("Primary_Dialect", ""),
                json.dumps(item.get("Primary_Crops", []), ensure_ascii=False),
                json.dumps(item.get("Top_3_Diseases", []), ensure_ascii=False),
                json.dumps(item.get("Symptom_Checklist_Offline", {}), ensure_ascii=False),
                json.dumps(item.get("Approved_Pesticide_Solution", {}), ensure_ascii=False),
            ))
            inserted_count += 1
        conn.commit()
    return inserted_count


# Auto-initialize database schema upon module import
init_db()

