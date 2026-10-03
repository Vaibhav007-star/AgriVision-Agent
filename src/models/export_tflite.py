"""
TFLite Model Exporter for AgriVision Mobile Deployment.
Converts the trained Keras MobileNetV2 model into an optimized TensorFlow Lite (.tflite) flatbuffer
and generates labels.txt for on-device inference on Flutter / Android / iOS.
"""

import os
import sys
from pathlib import Path
import json
import argparse
import numpy as np

# Suppress verbose TF messages
os.environ["TF_CPP_MIN_LOG_LEVEL"] = "3"
os.environ["TF_ENABLE_ONEDNN_OPTS"] = "0"
os.environ["KERAS_BACKEND"] = "tensorflow"

import keras
import tensorflow as tf

BASE_DIR = Path(__file__).resolve().parent.parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))


def export_model_to_tflite(
    keras_model_path: Path = None,
    output_tflite_path: Path = None,
    output_labels_path: Path = None,
    quantize: bool = True,
):
    """Loads .keras model and exports an optimized .tflite model and labels.txt."""
    if keras_model_path is None:
        keras_model_path = BASE_DIR / "models" / "saved_models" / "crop_disease_model.keras"
    if output_tflite_path is None:
        output_tflite_path = BASE_DIR / "models" / "saved_models" / "crop_disease_model.tflite"
    if output_labels_path is None:
        output_labels_path = BASE_DIR / "models" / "saved_models" / "labels.txt"

    if not keras_model_path.exists():
        raise FileNotFoundError(f"Model file not found at: {keras_model_path}")

    print(f"[*] Loading Keras model from: {keras_model_path}")
    model = keras.models.load_model(str(keras_model_path))

    print("[*] Initializing TensorFlow Lite Converter...")
    converter = tf.lite.TFLiteConverter.from_keras_model(model)
    if quantize:
        print("[+] Applying standard dynamic range / default optimizations...")
        converter.optimizations = [tf.lite.Optimize.DEFAULT]

    tflite_bytes = converter.convert()

    output_tflite_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_tflite_path, "wb") as f:
        f.write(tflite_bytes)

    size_mb = len(tflite_bytes) / (1024 * 1024)
    print(f"[+] TFLite model successfully saved: {output_tflite_path} ({size_mb:.2f} MB)")

    # Export labels.txt
    class_indices_path = keras_model_path.parent / "class_indices.json"
    if class_indices_path.exists():
        with open(class_indices_path, "r", encoding="utf-8") as f:
            class_indices = json.load(f)
        
        with open(output_labels_path, "w", encoding="utf-8") as f:
            for i in range(len(class_indices)):
                c_data = class_indices[str(i)]
                f.write(f"{c_data['class_name']}\n")
        print(f"[+] Exported {len(class_indices)} class labels to: {output_labels_path}")

    return output_tflite_path, output_labels_path


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Export AgriVision model to TFLite")
    parser.add_argument("--keras-path", type=Path, default=None)
    parser.add_argument("--out-tflite", type=Path, default=None)
    parser.add_argument("--out-labels", type=Path, default=None)
    parser.add_argument("--no-quant", action="store_true")

    args = parser.parse_args()
    export_model_to_tflite(
        keras_model_path=args.keras_path,
        output_tflite_path=args.out_tflite,
        output_labels_path=args.out_labels,
        quantize=not args.no_quant,
    )
