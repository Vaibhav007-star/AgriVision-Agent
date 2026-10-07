"""
Machine Learning Subpackage for AgriVision Agent (app/ml)
"""
try:
    from app.ml.model import build_custom_cnn, build_mobilenet_transfer_model
except Exception:
    build_custom_cnn = None
    build_mobilenet_transfer_model = None

from app.ml.inference import predict_crop_disease

