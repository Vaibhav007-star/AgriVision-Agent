"""
Model Training Script for AgriVision Agent (scripts/train.py).
Trains MobileNetV2 or Custom CNN on the configured dataset.
"""

import sys
from pathlib import Path

# Add project root to sys.path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from ml.training.train import train_model

if __name__ == "__main__":
    model_type = "MobileNetV2"
    if len(sys.argv) > 1:
        model_type = sys.argv[1]
    train_model(model_type)

