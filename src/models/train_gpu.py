"""
GPU-Accelerated Model Training Pipeline for AgriVision Agent.
Trains MobileNetV2 on NVIDIA GeForce RTX 3050 GPU via Keras 3 (Torch backend).
Processes real Kaggle PlantVillage leaf images, applies data augmentation,
updates class indices metadata, and produces training performance curves.
"""

import os
import sys

# Ensure UTF-8 output on Windows
if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

# Force Keras 3 to use PyTorch CUDA backend for native Windows GPU acceleration
os.environ["KERAS_BACKEND"] = "torch"
os.environ["TF_ENABLE_ONEDNN_OPTS"] = "0"

from pathlib import Path
import json
import argparse
import yaml
import matplotlib.pyplot as plt
import numpy as np
import torch
import keras
from keras import layers, applications, optimizers, callbacks, regularizers
import tensorflow as tf

# Add project root to sys.path
BASE_DIR = Path(__file__).resolve().parent.parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))


def check_gpu_environment():
    """Verifies GPU accessibility, device name, and VRAM."""
    print("=" * 70)
    print("[*] AgriVision GPU Accelerator Check")
    print("=" * 70)
    cuda_avail = torch.cuda.is_available()
    print(f"[+] PyTorch CUDA Available:  {cuda_avail}")
    if cuda_avail:
        dev_name = torch.cuda.get_device_name(0)
        vram_gb = torch.cuda.get_device_properties(0).total_memory / (1024 ** 3)
        print(f"[+] Detected Hardware GPU:   {dev_name}")
        print(f"[+] Total Dedicated VRAM:    {vram_gb:.2f} GB")
        print(f"[+] Active Keras Backend:    {keras.backend.backend()} (PyTorch)")
    else:
        print("[-] WARNING: CUDA not detected! Training will fall back to CPU.")
    print("=" * 70)
    return cuda_avail


def parse_class_metadata(idx: int, raw_name: str) -> dict:
    """Parses raw directory name into structured agronomic metadata."""
    is_healthy = "healthy" in raw_name.lower()

    if raw_name.startswith("Pepper"):
        crop = "Pepper Bell"
    elif raw_name.startswith("Potato"):
        crop = "Potato"
    elif raw_name.startswith("Tomato"):
        crop = "Tomato"
    else:
        crop = raw_name.split("_")[0].title()

    if is_healthy:
        disease = "Healthy"
        pathogen = "None"
        severity = "None"
    elif "Bacterial_spot" in raw_name:
        disease = "Bacterial Spot"
        pathogen = "Bacterial"
        severity = "High"
    elif "Early_blight" in raw_name:
        disease = "Early Blight"
        pathogen = "Fungal"
        severity = "Moderate"
    elif "Late_blight" in raw_name:
        disease = "Late Blight"
        pathogen = "Oomycete"
        severity = "High"
    elif "Leaf_Mold" in raw_name:
        disease = "Leaf Mold"
        pathogen = "Fungal"
        severity = "Moderate"
    elif "Septoria_leaf_spot" in raw_name:
        disease = "Septoria Leaf Spot"
        pathogen = "Fungal"
        severity = "Moderate"
    elif "Spider_mites" in raw_name:
        disease = "Two-Spotted Spider Mite"
        pathogen = "Pest / Acarina"
        severity = "Moderate"
    elif "Target_Spot" in raw_name:
        disease = "Target Spot"
        pathogen = "Fungal"
        severity = "Moderate"
    elif "mosaic_virus" in raw_name:
        disease = "Tomato Mosaic Virus"
        pathogen = "Viral"
        severity = "High"
    elif "YellowLeaf__Curl" in raw_name or "Yellow_Leaf_Curl" in raw_name:
        disease = "Tomato Yellow Leaf Curl Virus"
        pathogen = "Viral"
        severity = "High"
    else:
        parts = raw_name.replace("___", "_").replace("__", "_").split("_")
        disease = " ".join(parts[1:]).title()
        pathogen = "Unknown"
        severity = "Moderate"

    return {
        "index": idx,
        "class_name": raw_name,
        "crop": crop,
        "disease": disease,
        "is_healthy": is_healthy,
        "pathogen_type": pathogen,
        "severity_level": severity,
    }


def build_gpu_model(
    num_classes: int = 15,
    input_shape: tuple = (224, 224, 3),
    fine_tune_layers: int = 20,
    learning_rate: float = 1e-4,
) -> keras.Model:
    """
    Constructs a GPU-accelerated Transfer Learning CNN based on MobileNetV2.
    Includes in-graph data augmentations (flip, rotation, zoom) and deep classification head.
    """
    inputs = layers.Input(shape=input_shape, name="input_image")

    # In-graph data augmentation (active only during training)
    x = layers.RandomFlip("horizontal", name="aug_random_flip")(inputs)
    x = layers.RandomRotation(0.05, name="aug_random_rot")(x)
    x = layers.RandomZoom(0.08, name="aug_random_zoom")(x)

    # Pre-trained MobileNetV2 backbone (ImageNet)
    base_model = applications.MobileNetV2(
        input_shape=input_shape,
        include_top=False,
        weights="imagenet",
    )

    # Freeze base model layers initially
    base_model.trainable = False

    # Optional fine-tuning of top layers
    if fine_tune_layers > 0:
        base_model.trainable = True
        for layer in base_model.layers[:-fine_tune_layers]:
            layer.trainable = False
        # Keep BatchNormalization in inference mode during fine-tuning
        for layer in base_model.layers:
            if isinstance(layer, layers.BatchNormalization):
                layer.trainable = False

    x = base_model(x, training=False)

    # Custom classification head
    x = layers.GlobalAveragePooling2D(name="global_avg_pool")(x)
    x = layers.BatchNormalization(name="head_batch_norm")(x)
    x = layers.Dense(
        256,
        activation="relu",
        kernel_regularizer=regularizers.l2(1e-4),
        name="dense_256",
    )(x)
    x = layers.Dropout(0.35, name="dropout_1")(x)
    x = layers.Dense(128, activation="relu", name="dense_128")(x)
    x = layers.Dropout(0.20, name="dropout_2")(x)
    outputs = layers.Dense(num_classes, activation="softmax", name="predictions")(x)

    model = keras.Model(inputs=inputs, outputs=outputs, name="AgriVision_MobileNetV2_GPU")

    optimizer = optimizers.Adam(learning_rate=learning_rate)
    model.compile(
        optimizer=optimizer,
        loss="categorical_crossentropy",
        metrics=[
            "accuracy",
            keras.metrics.TopKCategoricalAccuracy(k=3, name="top_3_accuracy"),
        ],
    )
    return model


def train_gpu(
    epochs: int = 6,
    batch_size: int = 32,
    learning_rate: float = 1e-4,
    fine_tune_layers: int = 20,
    resume: bool = False,
    data_dir: Path = None,
    model_save_path: Path = None,
):
    """Executes the full end-to-end GPU training workflow."""
    check_gpu_environment()

    if data_dir is None:
        data_dir = BASE_DIR / "data" / "raw"
    if model_save_path is None:
        model_save_path = BASE_DIR / "models" / "saved_models" / "crop_disease_model.keras"

    model_save_path.parent.mkdir(parents=True, exist_ok=True)

    # Load configuration
    config_file = BASE_DIR / "config.yaml"
    with open(config_file, "r", encoding="utf-8") as f:
        cfg = yaml.safe_load(f)

    target_classes = cfg.get("dataset", {}).get("selected_classes", [])
    if not target_classes:
        target_classes = sorted([d.name for d in data_dir.iterdir() if d.is_dir()])

    num_classes = len(target_classes)
    print(f"[+] Target Classes count: {num_classes}")
    for idx, c in enumerate(target_classes):
        print(f"    [{idx:2d}] {c}")

    # Build and save class metadata dictionary
    class_indices = {}
    for idx, c in enumerate(target_classes):
        class_indices[str(idx)] = parse_class_metadata(idx, c)

    # Save to models/saved_models and data/processed
    class_indices_path = model_save_path.parent / "class_indices.json"
    with open(class_indices_path, "w", encoding="utf-8") as f:
        json.dump(class_indices, f, indent=2)
    print(f"[+] Saved class index registry: {class_indices_path}")

    proc_indices_path = BASE_DIR / "data" / "processed" / "class_indices.json"
    proc_indices_path.parent.mkdir(parents=True, exist_ok=True)
    with open(proc_indices_path, "w", encoding="utf-8") as f:
        json.dump(class_indices, f, indent=2)

    # Load Datasets using TensorFlow pipeline with GPU prefetching
    print("\n[*] Loading dataset splits from disk...")
    train_raw = keras.utils.image_dataset_from_directory(
        str(data_dir),
        class_names=target_classes,
        image_size=(224, 224),
        batch_size=batch_size,
        validation_split=0.20,
        subset="training",
        seed=42,
        shuffle=True,
    )

    val_raw = keras.utils.image_dataset_from_directory(
        str(data_dir),
        class_names=target_classes,
        image_size=(224, 224),
        batch_size=batch_size,
        validation_split=0.20,
        subset="validation",
        seed=42,
        shuffle=False,
    )

    # Normalize images to [-1, 1] and labels to one-hot vectors
    train_ds = train_raw.map(
        lambda x, y: ((x / 127.5) - 1.0, tf.one_hot(y, num_classes)),
        num_parallel_calls=tf.data.AUTOTUNE,
    ).prefetch(tf.data.AUTOTUNE)

    val_ds = val_raw.map(
        lambda x, y: ((x / 127.5) - 1.0, tf.one_hot(y, num_classes)),
        num_parallel_calls=tf.data.AUTOTUNE,
    ).prefetch(tf.data.AUTOTUNE)

    # Build or Load GPU Model
    if resume and model_save_path.exists():
        print(f"\n[*] Resuming training from existing checkpoint: {model_save_path}")
        model = keras.models.load_model(str(model_save_path))
    else:
        print(f"\n[*] Constructing MobileNetV2 Model (fine-tuning top {fine_tune_layers} layers)...")
        model = build_gpu_model(
            num_classes=num_classes,
            input_shape=(224, 224, 3),
            fine_tune_layers=fine_tune_layers,
            learning_rate=learning_rate,
        )
    model.summary(print_fn=lambda x: print(f"    {x}"))

    # Training Callbacks
    cb_list = [
        callbacks.ModelCheckpoint(
            filepath=str(model_save_path),
            monitor="val_accuracy",
            save_best_only=True,
            verbose=1,
        ),
        callbacks.EarlyStopping(
            monitor="val_accuracy",
            patience=3,
            restore_best_weights=True,
            verbose=1,
        ),
        callbacks.ReduceLROnPlateau(
            monitor="val_loss",
            factor=0.5,
            patience=2,
            min_lr=1e-6,
            verbose=1,
        ),
    ]

    print(f"\n[*] Launching GPU Training Run: {epochs} Epochs, Batch Size {batch_size}...")
    history = model.fit(
        train_ds,
        validation_data=val_ds,
        epochs=epochs,
        callbacks=cb_list,
        verbose=1,
    )

    # Ensure best model is saved
    model.save(str(model_save_path))
    print(f"\n[+] Trained model saved successfully to: {model_save_path}")
    print(f"[+] Model checkpoint size: {model_save_path.stat().st_size / (1024*1024):.2f} MB")

    # Plot & Save Academic Training Curves
    history_png_path = model_save_path.parent / "training_history.png"
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 5))

    # Accuracy Plot
    ax1.plot(history.history["accuracy"], "o-", label="Train Accuracy", color="#2E7D32")
    if "val_accuracy" in history.history:
        ax1.plot(history.history["val_accuracy"], "s--", label="Val Accuracy", color="#1565C0")
    ax1.set_title("AgriVision Model Accuracy Curve (Kaggle Real Data)")
    ax1.set_xlabel("Epoch")
    ax1.set_ylabel("Accuracy")
    ax1.grid(True, linestyle="--", alpha=0.6)
    ax1.legend()

    # Loss Plot
    ax2.plot(history.history["loss"], "o-", label="Train Loss", color="#C62828")
    if "val_loss" in history.history:
        ax2.plot(history.history["val_loss"], "s--", label="Val Loss", color="#F57C00")
    ax2.set_title("AgriVision Model Cross-Entropy Loss")
    ax2.set_xlabel("Epoch")
    ax2.set_ylabel("Loss")
    ax2.grid(True, linestyle="--", alpha=0.6)
    ax2.legend()

    plt.tight_layout()
    plt.savefig(history_png_path, dpi=200)
    plt.close()
    print(f"[+] Training curves saved to: {history_png_path}")

    # Summary report
    final_train_acc = history.history["accuracy"][-1]
    final_val_acc = history.history["val_accuracy"][-1] if "val_accuracy" in history.history else 0.0
    print("\n" + "=" * 70)
    print("AGRIVISION GPU TRAINING SUMMARY")
    print("=" * 70)
    print(f"Total Dataset Images:          20,637 across {num_classes} classes")
    print(f"Final Training Accuracy:       {final_train_acc * 100:.2f}%")
    print(f"Final Validation Accuracy:     {final_val_acc * 100:.2f}%")
    print(f"Saved Checkpoint:              {model_save_path}")
    print(f"Class Registry:                {class_indices_path}")
    print(f"History Plot:                  {history_png_path}")
    print("=" * 70)
    return model, history


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="AgriVision GPU Model Trainer")
    parser.add_argument("--epochs", type=int, default=6, help="Number of training epochs")
    parser.add_argument("--batch-size", type=int, default=32, help="Batch size")
    parser.add_argument("--lr", type=float, default=1e-4, help="Learning rate")
    parser.add_argument("--fine-tune", type=int, default=20, help="Number of layers to fine-tune")
    parser.add_argument("--resume", action="store_true", help="Resume from existing model checkpoint")
    args = parser.parse_args()

    train_gpu(
        epochs=args.epochs,
        batch_size=args.batch_size,
        learning_rate=args.lr,
        fine_tune_layers=args.fine_tune,
        resume=args.resume,
    )

