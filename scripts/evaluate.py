"""
Model Evaluation Script for AgriVision Agent (scripts/evaluate.py).
Evaluates trained models and generates confusion matrix and classification reports.
"""

import sys
from pathlib import Path

# Add project root to sys.path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from ml.evaluation.evaluate import evaluate_model

if __name__ == "__main__":
    evaluate_model()

