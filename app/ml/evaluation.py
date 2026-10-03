"""
Model Evaluation and Metrics Computation Module (app/ml/evaluation.py).
"""

from typing import Dict, Any, Optional
from pathlib import Path
from ml.evaluation.evaluate import evaluate_model

BASE_DIR = Path(__file__).resolve().parent.parent.parent


def run_evaluation(model_path: Optional[Path] = None) -> Dict[str, Any]:
    """Runs evaluation over the held-out test split."""
    return evaluate_model(model_path=model_path)

