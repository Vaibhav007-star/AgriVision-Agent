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
        
        conn.commit()


# Auto-initialize database schema upon module import
init_db()

