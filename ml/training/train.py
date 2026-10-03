"""
Training Engine for AgriVision Agent CNN and Transfer Learning Models.
Reads config.yaml, loads train/val datasets, trains models with callbacks,
and saves model checkpoints and training history curves to reports/.
"""

from typing import Dict, Any, Tuple, Optional
import os
import sys
from pathlib import Path
import json
import yaml
import numpy as np
import matplotlib.pyplot as plt
import tensorflow as tf
from tensorflow.keras.callbacks import EarlyStopping, ModelCheckpoint, ReduceLROnPlateau

# Ensure project root is in sys.path
BASE_DIR = Path(__file__).resolve().parent.parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from ml.models.custom_cnn import build_custom_cnn
from ml.models.mobilenet_model import build_mobilenetv2_model

if sys.stdout.encoding != 'utf-8':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass


def load_config(config_path: Optional[Path] = None) -> Dict[str, Any]:
    """Loads configuration from config.yaml."""
    if config_path is None:
        config_path = BASE_DIR / "config.yaml"
    with open(config_path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def prepare_datasets(
    processed_dir: Path,
    image_size: Tuple[int, int] = (224, 224),
    batch_size: int = 16
) -> Tuple[tf.data.Dataset, tf.data.Dataset, list]:
    """
    Loads train and validation datasets from processed directories,
    applying normalization to [-1.0, 1.0].
    """
    train_dir = processed_dir / "train"
    val_dir = processed_dir / "val"
    
    if not train_dir.exists() or not val_dir.exists():
        raise FileNotFoundError(f"Processed dataset directories not found in: {processed_dir}")
        
    train_ds = tf.keras.utils.image_dataset_from_directory(
        train_dir,
        image_size=image_size,
        batch_size=batch_size,
        label_mode="categorical",
        shuffle=True,
        seed=42
    )
    
    val_ds = tf.keras.utils.image_dataset_from_directory(
        val_dir,
        image_size=image_size,
        batch_size=batch_size,
        label_mode="categorical",
        shuffle=False
    )
    
    class_names = train_ds.class_names
    
    # Normalization layer: [0, 255] -> [-1, 1]
    rescaling = tf.keras.layers.Rescaling(1./127.5, offset=-1.0)
    train_ds = train_ds.map(lambda x, y: (rescaling(x), y), num_parallel_calls=tf.data.AUTOTUNE)
    val_ds = val_ds.map(lambda x, y: (rescaling(x), y), num_parallel_calls=tf.data.AUTOTUNE)
    
    train_ds = train_ds.prefetch(buffer_size=tf.data.AUTOTUNE)
    val_ds = val_ds.prefetch(buffer_size=tf.data.AUTOTUNE)
    
    return train_ds, val_ds, class_names


def plot_training_curves(history: tf.keras.callbacks.History, reports_dir: Path, model_name: str) -> None:
    """Generates and saves training accuracy and loss curves."""
    reports_dir.mkdir(parents=True, exist_ok=True)
    
    acc = history.history.get("accuracy", [])
    val_acc = history.history.get("val_accuracy", [])
    loss = history.history.get("loss", [])
    val_loss = history.history.get("val_loss", [])
    epochs_range = range(1, len(acc) + 1)
    
    # 1. Accuracy Curve
    plt.figure(figsize=(8, 5))
    plt.plot(epochs_range, acc, label="Training Accuracy", color="#2e7d32", lw=2)
    if val_acc:
        plt.plot(epochs_range, val_acc, label="Validation Accuracy", color="#1565c0", lw=2, linestyle="--")
    plt.title(f"{model_name} - Training & Validation Accuracy", fontsize=12, fontweight="bold")
    plt.xlabel("Epoch", fontsize=10)
    plt.ylabel("Categorical Accuracy", fontsize=10)
    plt.legend(loc="lower right")
    plt.grid(True, linestyle=":", alpha=0.6)
    plt.tight_layout()
    plt.savefig(reports_dir / "training_accuracy.png", dpi=200)
    plt.close()
    
    # 2. Loss Curve
    plt.figure(figsize=(8, 5))
    plt.plot(epochs_range, loss, label="Training Loss", color="#c62828", lw=2)
    if val_loss:
        plt.plot(epochs_range, val_loss, label="Validation Loss", color="#f57f17", lw=2, linestyle="--")
    plt.title(f"{model_name} - Training & Validation Loss", fontsize=12, fontweight="bold")
    plt.xlabel("Epoch", fontsize=10)
    plt.ylabel("Categorical Crossentropy Loss", fontsize=10)
    plt.legend(loc="upper right")
    plt.grid(True, linestyle=":", alpha=0.6)
    plt.tight_layout()
    plt.savefig(reports_dir / "training_loss.png", dpi=200)
    plt.close()


def train_model(
    model_type: str = "MobileNetV2",
    config_path: Optional[Path] = None
) -> Dict[str, Any]:
    """
    Trains the specified deep learning model (MobileNetV2 or CustomCNN)
    on the processed development dataset.
    """
    cfg = load_config(config_path)
    dataset_cfg = cfg["dataset"]
    model_cfg = cfg["model"]
    
    processed_dir = BASE_DIR / dataset_cfg["processed_dir"]
    reports_dir = BASE_DIR / "reports"
    models_dir = BASE_DIR / "models"
    models_dir.mkdir(parents=True, exist_ok=True)
    (models_dir / "saved_models").mkdir(parents=True, exist_ok=True)
    
    image_size = tuple(dataset_cfg.get("image_size", [224, 224]))
    batch_size = model_cfg.get("batch_size", 16)
    epochs = model_cfg.get("epochs", 10)
    lr = model_cfg.get("learning_rate", 0.0001)
    
    print("=" * 70)
    print(f"🌾 AgriVision Agent — Model Training Pipeline ({model_type})")
    print("=" * 70)
    print(f"Dataset Path:  {processed_dir}")
    print(f"Batch Size:    {batch_size}")
    print(f"Target Epochs: {epochs}")
    print(f"Learning Rate: {lr}")
    print("-" * 70)
    
    train_ds, val_ds, class_names = prepare_datasets(processed_dir, image_size, batch_size)
    num_classes = len(class_names)
    print(f"Loaded {num_classes} classes: {', '.join(class_names)}")
    
    # Save class names mapping
    class_names_path = models_dir / "class_names.json"
    with open(class_names_path, "w", encoding="utf-8") as f:
        json.dump(class_names, f, indent=2)
        
    # Build model architecture
    if model_type.lower() == "customcnn":
        model = build_custom_cnn(num_classes=num_classes, input_shape=(*image_size, 3), learning_rate=lr)
        save_name = "cnn_model.keras"
    else:
        model = build_mobilenetv2_model(
            num_classes=num_classes,
            input_shape=(*image_size, 3),
            fine_tune_layers=model_cfg.get("fine_tune_layers", 20),
            learning_rate=lr,
            dropout_rate=model_cfg.get("dropout_rate", 0.35)
        )
        save_name = "mobilenet_model.keras"
        
    model_save_path = models_dir / save_name
    prod_save_path = models_dir / "saved_models" / "crop_disease_model.keras"
    
    callbacks = [
        EarlyStopping(monitor="val_loss", patience=4, restore_best_weights=True, verbose=1),
        ReduceLROnPlateau(monitor="val_loss", factor=0.3, patience=2, min_lr=1e-6, verbose=1),
        ModelCheckpoint(filepath=str(model_save_path), monitor="val_accuracy", save_best_only=True, verbose=1)
    ]
    
    print("\n[Training Start] Executing genuine transfer learning epochs...")
    history = model.fit(
        train_ds,
        validation_data=val_ds,
        epochs=epochs,
        callbacks=callbacks,
        verbose=1
    )
    
    # Save final model checkpoints
    model.save(str(model_save_path))
    model.save(str(prod_save_path))
    print(f"\n[+] Saved trained model checkpoint to: {model_save_path}")
    print(f"[+] Saved active production model to:    {prod_save_path}")
    
    # Plot history curves
    plot_training_curves(history, reports_dir, model_type)
    print(f"[+] Saved training history curves to:    {reports_dir}")
    
    # Format class indices for production inference
    prod_class_indices = {}
    for idx, c in enumerate(class_names):
        prod_class_indices[str(idx)] = {
            "index": idx,
            "class_name": c,
            "crop": c.split("___")[0].replace("_", " ").title() if "___" in c else c,
            "disease": c.split("___")[1].replace("_", " ").title() if "___" in c else "Unknown",
            "is_healthy": "healthy" in c.lower()
        }
    with open(models_dir / "saved_models" / "class_indices.json", "w", encoding="utf-8") as f:
        json.dump(prod_class_indices, f, indent=2)
        
    print("=" * 70)
    return {
        "model_type": model_type,
        "history": history.history,
        "class_names": class_names,
        "model_path": str(model_save_path)
    }


if __name__ == "__main__":
    train_model("MobileNetV2")
