"""
Configuration module for AgriVision Agent.
Loads settings from environment variables and provides structured access.
"""

import os
from pathlib import Path
from dataclasses import dataclass
from dotenv import load_dotenv

# Base project directory
BASE_DIR = Path(__file__).resolve().parent.parent

# Load .env file if present
ENV_PATH = BASE_DIR / ".env"
if ENV_PATH.exists():
    load_dotenv(dotenv_path=ENV_PATH)
else:
    load_dotenv()  # fallback to standard search


@dataclass(frozen=True)
class AppConfig:
    """Core Application Settings."""
    APP_NAME: str = "AgriVision Agent"
    APP_VERSION: str = "1.0.0"
    APP_ENV: str = os.getenv("APP_ENV", "development")
    APP_DEBUG: bool = os.getenv("APP_DEBUG", "True").lower() in ("true", "1", "yes")
    APP_PORT: int = int(os.getenv("APP_PORT", 8501))
    DEFAULT_LANGUAGE: str = os.getenv("DEFAULT_LANGUAGE", "en")


@dataclass(frozen=True)
class LLMConfig:
    """LLM Provider and Model Configuration."""
    PROVIDER: str = os.getenv("LLM_PROVIDER", "groq").lower()
    
    # Groq configuration (free, ultra-fast)
    GROQ_API_KEY: str = os.getenv("GROQ_API_KEY", "")
    GROQ_MODEL: str = os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile")
    
    # Gemini configuration (free tier)
    GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY", "")
    GEMINI_MODEL: str = os.getenv("GEMINI_MODEL", "gemini-1.5-flash")
    
    # Ollama local configuration (offline)
    OLLAMA_BASE_URL: str = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
    OLLAMA_MODEL: str = os.getenv("OLLAMA_MODEL", "llama3.2:latest")


@dataclass(frozen=True)
class ModelConfig:
    """Deep Learning & Computer Vision Configuration."""
    MODEL_PATH: Path = BASE_DIR / os.getenv("MODEL_PATH", "models/saved_models/crop_disease_model.keras")
    CLASS_INDICES_PATH: Path = BASE_DIR / os.getenv("CLASS_INDICES_PATH", "models/saved_models/class_indices.json")
    CONFIDENCE_THRESHOLD: float = float(os.getenv("CONFIDENCE_THRESHOLD", 0.60))
    INPUT_IMAGE_SIZE: int = int(os.getenv("INPUT_IMAGE_SIZE", 224))
    BATCH_SIZE: int = int(os.getenv("BATCH_SIZE", 32))


@dataclass(frozen=True)
class RAGConfig:
    """RAG and Vector DB Configuration."""
    RAG_DATA_DIR: Path = BASE_DIR / os.getenv("RAG_DATA_DIR", "data/rag_docs")
    FAISS_INDEX_PATH: Path = BASE_DIR / os.getenv("FAISS_INDEX_PATH", "data/processed/faiss_index")
    EMBEDDING_MODEL: str = os.getenv("EMBEDDING_MODEL", "sentence-transformers/all-MiniLM-L6-v2")
    TOP_K_RETRIEVAL: int = int(os.getenv("TOP_K_RETRIEVAL", 3))


@dataclass(frozen=True)
class ExternalServicesConfig:
    """External Tools / APIs Configuration."""
    WEATHER_API_KEY: str = os.getenv("WEATHER_API_KEY", "")
    DEFAULT_LOCATION: str = os.getenv("DEFAULT_LOCATION", "New Delhi, India")
    DATABASE_URL: str = os.getenv("DATABASE_URL", f"sqlite:///{BASE_DIR / 'data' / 'agrivision.db'}")


# Global Config Container
class Config:
    """Master Configuration class holding sub-configs."""
    app = AppConfig()
    llm = LLMConfig()
    model = ModelConfig()
    rag = RAGConfig()
    services = ExternalServicesConfig()
    base_dir = BASE_DIR


config = Config()

