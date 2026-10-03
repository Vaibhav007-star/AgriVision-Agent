"""
Data Models and Typed Schemas for SQLite Storage.
"""

from typing import Dict, Any, Optional, List
from dataclasses import dataclass
import json


@dataclass
class PredictionRecord:
    """Represents a crop diagnosis prediction log entry."""
    crop: str
    disease: str
    confidence: float
    prediction_id: Optional[int] = None
    timestamp: Optional[str] = None
    crop_stage: str = "Vegetative"
    language: str = "en"
    recommendation: Optional[str] = None
    image_path: Optional[str] = None
    weather_context: Optional[str] = None
    treatment: Optional[str] = None
    prevention: Optional[str] = None
    top3_json: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "prediction_id": self.prediction_id,
            "timestamp": self.timestamp,
            "crop": self.crop,
            "disease": self.disease,
            "confidence": self.confidence,
            "crop_stage": self.crop_stage,
            "language": self.language,
            "recommendation": self.recommendation,
            "image_path": self.image_path,
            "weather_context": self.weather_context,
            "treatment": self.treatment,
            "prevention": self.prevention,
            "top3_json": self.top3_json
        }

