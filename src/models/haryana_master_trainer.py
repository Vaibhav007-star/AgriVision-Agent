"""
Haryana Master Multi-Crop Unified Classifier Trainer (src/models/haryana_master_trainer.py).

Trains a unified deep learning vision model (MobileNetV2) across ALL 33 crop disease
classes cultivated across all 22 districts of Haryana:
- Wheat (4 classes)
- Rice (3 classes)
- Cotton (4 classes)
- Sugarcane (5 classes)
- Corn / Maize (2 classes)
- Vegetables & Tubers: Tomato, Potato, Pepper Bell (15 classes)

Hardware Acceleration:
- Fully accelerated on NVIDIA GeForce RTX 3050 6GB Laptop GPU using PyTorch CUDA (cu121).
- Automatic Mixed Precision (AMP FP16) for accelerated tensor core throughput.
- Exports trained model to PyTorch (.pt) and ONNX (.onnx) for edge execution.
"""

import os
import sys
import time
import json
import shutil
from pathlib import Path
from typing import Dict, List, Any, Tuple

if sys.stdout.encoding != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')

import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import DataLoader
from torchvision import datasets, transforms
from torchvision.models import mobilenet_v2, MobileNet_V2_Weights

BASE_DIR = Path("c:/Projects/AgriVision Agent")
CURRICULUM_DIR = BASE_DIR / "data" / "haryana_curriculum"
UNIFIED_DATA_DIR = BASE_DIR / "data" / "haryana_unified_master"
MODEL_DIR = BASE_DIR / "models" / "haryana_models"

MODEL_DIR.mkdir(parents=True, exist_ok=True)


def build_unified_dataset():
    """Aggregates all curriculum crop splits into a single master dataset."""
    train_dest = UNIFIED_DATA_DIR / "train"
    val_dest = UNIFIED_DATA_DIR / "val"
    
    if train_dest.exists() and len(list(train_dest.iterdir())) >= 30:
        print(f"Unified dataset already assembled with {len(list(train_dest.iterdir()))} classes.")
        return
        
    print(f"Building unified multi-crop dataset in {UNIFIED_DATA_DIR}...")
    train_dest.mkdir(parents=True, exist_ok=True)
    val_dest.mkdir(parents=True, exist_ok=True)
    
    for crop_dir in CURRICULUM_DIR.iterdir():
        if not crop_dir.is_dir():
            continue
        crop_train = crop_dir / "train"
        crop_val = crop_dir / "val"
        
        if crop_train.exists():
            for class_dir in crop_train.iterdir():
                if class_dir.is_dir():
                    target = train_dest / class_dir.name
                    target.mkdir(parents=True, exist_ok=True)
                    for img in class_dir.iterdir():
                        if img.is_file():
                            shutil.copy2(img, target / img.name)
                            
        if crop_val.exists():
            for class_dir in crop_val.iterdir():
                if class_dir.is_dir():
                    target = val_dest / class_dir.name
                    target.mkdir(parents=True, exist_ok=True)
                    for img in class_dir.iterdir():
                        if img.is_file():
                            shutil.copy2(img, target / img.name)
                            
    print(f"Assembled {len(list(train_dest.iterdir()))} total disease classes!")


def train_master_model(epochs: int = 3, batch_size: int = 32):
    build_unified_dataset()
    
    device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")
    print(f"\n=======================================================")
    print(f"🚀 Training Haryana Master Multi-Crop Model on: {device}")
    if device.type == "cuda":
        print(f"   Device Name: {torch.cuda.get_device_name(0)}")
    print(f"=======================================================\n")
    
    train_tf = transforms.Compose([
        transforms.Resize((224, 224)),
        transforms.RandomHorizontalFlip(),
        transforms.RandomVerticalFlip(p=0.3),
        transforms.RandomRotation(degrees=15),
        transforms.ColorJitter(brightness=0.15, contrast=0.15),
        transforms.ToTensor(),
        transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
    ])
    val_tf = transforms.Compose([
        transforms.Resize((224, 224)),
        transforms.ToTensor(),
        transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
    ])
    
    train_ds = datasets.ImageFolder(str(UNIFIED_DATA_DIR / "train"), transform=train_tf)
    val_ds = datasets.ImageFolder(str(UNIFIED_DATA_DIR / "val"), transform=val_tf)
    
    class_names = train_ds.classes
    num_classes = len(class_names)
    print(f"Classes ({num_classes}): {class_names}")
    print(f"Samples: {len(train_ds)} train | {len(val_ds)} val\n")
    
    train_loader = DataLoader(train_ds, batch_size=batch_size, shuffle=True, num_workers=0, pin_memory=(device.type == 'cuda'))
    val_loader = DataLoader(val_ds, batch_size=batch_size, shuffle=False, num_workers=0)
    
    weights = MobileNet_V2_Weights.DEFAULT
    model = mobilenet_v2(weights=weights)
    for param in model.features[:10].parameters():
        param.requires_grad = False
        
    in_features = model.classifier[1].in_features
    model.classifier = nn.Sequential(
        nn.Dropout(p=0.3),
        nn.Linear(in_features, 512),
        nn.ReLU(),
        nn.Dropout(p=0.2),
        nn.Linear(512, num_classes)
    )
    model = model.to(device)
    
    criterion = nn.CrossEntropyLoss()
    optimizer = optim.AdamW(model.parameters(), lr=1e-3, weight_decay=1e-4)
    scaler = torch.amp.GradScaler('cuda', enabled=(device.type == 'cuda'))
    scheduler = optim.lr_scheduler.CosineAnnealingLR(optimizer, T_max=epochs)
    
    start_time = time.time()
    best_acc = 0.0
    
    for epoch in range(1, epochs + 1):
        model.train()
        train_loss = 0.0
        train_correct = 0
        train_total = 0
        
        for images, labels in train_loader:
            images = images.to(device, non_blocking=True)
            labels = labels.to(device, non_blocking=True)
            
            optimizer.zero_grad()
            with torch.amp.autocast('cuda', enabled=(device.type == 'cuda')):
                outputs = model(images)
                loss = criterion(outputs, labels)
                
            scaler.scale(loss).backward()
            scaler.step(optimizer)
            scaler.update()
            
            train_loss += loss.item() * images.size(0)
            _, preds = torch.max(outputs, 1)
            train_correct += (preds == labels).sum().item()
            train_total += labels.size(0)
            
        scheduler.step()
        train_acc = (train_correct / max(1, train_total)) * 100.0
        train_l = train_loss / max(1, train_total)
        
        model.eval()
        val_loss = 0.0
        val_correct = 0
        val_total = 0
        
        with torch.no_grad():
            for images, labels in val_loader:
                images = images.to(device, non_blocking=True)
                labels = labels.to(device, non_blocking=True)
                
                with torch.amp.autocast('cuda', enabled=(device.type == 'cuda')):
                    outputs = model(images)
                    loss = criterion(outputs, labels)
                    
                val_loss += loss.item() * images.size(0)
                _, preds = torch.max(outputs, 1)
                val_correct += (preds == labels).sum().item()
                val_total += labels.size(0)
                
        val_acc = (val_correct / max(1, val_total)) * 100.0
        val_l = val_loss / max(1, val_total)
        
        if val_acc > best_acc:
            best_acc = val_acc
            
        print(f"[Master Epoch {epoch}/{epochs}] "
              f"Train Loss: {train_l:.4f} | Acc: {train_acc:.1f}% || "
              f"Val Loss: {val_l:.4f} | Acc: {val_acc:.1f}%")
              
    elapsed = time.time() - start_time
    print(f"\nTraining completed in {elapsed:.1f}s! Best Accuracy: {best_acc:.2f}%")
    
    # Save PyTorch Model
    pt_path = MODEL_DIR / "haryana_master_multicrop_gpu.pt"
    torch.save({
        "num_classes": num_classes,
        "class_names": class_names,
        "model_state_dict": model.state_dict(),
        "best_accuracy": best_acc
    }, pt_path)
    print(f"Saved PyTorch Checkpoint to: {pt_path}")
    
    # Save Class Map
    map_path = MODEL_DIR / "haryana_class_map.json"
    with open(map_path, "w") as f:
        json.dump({str(i): c for i, c in enumerate(class_names)}, f, indent=2)
    print(f"Saved Class Map to: {map_path}")
    
    # Export to ONNX
    try:
        model.eval()
        dummy_input = torch.randn(1, 3, 224, 224, device=device)
        onnx_path = MODEL_DIR / "haryana_master_model.onnx"
        torch.onnx.export(
            model,
            dummy_input,
            str(onnx_path),
            input_names=["input"],
            output_names=["output"],
            dynamic_axes={"input": {0: "batch_size"}, "output": {0: "batch_size"}},
            opset_version=14
        )
        print(f"Saved ONNX Model to: {onnx_path}")
    except Exception as e:
        print(f"Notice: ONNX export skipped ({e})")


if __name__ == "__main__":
    epochs = int(sys.argv[1]) if len(sys.argv) > 1 else 3
    train_master_model(epochs=epochs)
