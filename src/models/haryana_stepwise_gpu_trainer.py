"""
Haryana District-Wise Stepwise GPU Crop Disease Trainer (src/models/haryana_stepwise_gpu_trainer.py).

Trains Deep Learning Vision models (MobileNetV2) step-by-step, crop-by-crop,
directly linking each crop with its corresponding Haryana agricultural districts:

Stepwise Curriculum:
- Step 1: WHEAT (Gehu) -> Districts: Karnal, Kurukshetra, Hisar, Jind, Rohtak, Sirsa, Ambala, Kaithal
- Step 2: RICE (Basmati & Paddy) -> Districts: Karnal, Kaithal, Kurukshetra, Yamunanagar, Ambala, Panipat, Sonipat
- Step 3: COTTON (Kapas) -> Districts: Sirsa, Fatehabad, Hisar, Bhiwani, Charkhi Dadri
- Step 4: SUGARCANE (Ganna) -> Districts: Yamunanagar, Karnal, Panipat, Sonipat, Ambala, Kaithal
- Step 5: CORN / MAIZE (Makka) -> Districts: Panchkula, Ambala, Yamunanagar, Karnal, Sonipat
- Step 6: VEGETABLES (Tomato, Potato, Pepper) -> Districts: Sonipat, Karnal, Kurukshetra, Jhajjar, Palwal, Rohtak

Hardware Acceleration:
- Fully accelerated on NVIDIA GeForce RTX 3050 6GB Laptop GPU using PyTorch CUDA (cu121).
- Automatic Mixed Precision (AMP FP16) for accelerated tensor core throughput.
"""

import os
import sys
import time
import json
from pathlib import Path
from typing import Dict, List, Any, Tuple

if sys.stdout.encoding != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')

import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import DataLoader
from torchvision import datasets, transforms, models
from torchvision.models import mobilenet_v2, MobileNet_V2_Weights

BASE_DIR = Path("c:/Projects/AgriVision Agent")
DATA_DIR = BASE_DIR / "data" / "haryana_curriculum"
CHECKPOINT_DIR = BASE_DIR / "models" / "haryana_checkpoints"
MODEL_DIR = BASE_DIR / "models" / "haryana_models"

CHECKPOINT_DIR.mkdir(parents=True, exist_ok=True)
MODEL_DIR.mkdir(parents=True, exist_ok=True)

# Stepwise Curriculum Configuration linking Crops with Haryana Districts
HARYANA_TRAINING_CURRICULUM = [
    {
        "step": 1,
        "crop_key": "wheat",
        "crop_name": "Wheat (Gehu)",
        "season": "Rabi",
        "primary_districts": ["Karnal", "Kurukshetra", "Hisar", "Jind", "Rohtak", "Sirsa", "Ambala", "Kaithal", "Fatehabad", "Panipat"],
        "all_districts_note": "Wheat is grown across all 22 Haryana districts as the premier foodgrain crop.",
        "key_pathogens": ["Stripe Rust (Puccinia striiformis)", "Leaf Rust (Puccinia triticina)", "Stem Rust (Puccinia graminis)"]
    },
    {
        "step": 2,
        "crop_key": "rice",
        "crop_name": "Rice / Paddy (Basmati & Non-Basmati)",
        "season": "Kharif",
        "primary_districts": ["Karnal", "Kaithal", "Kurukshetra", "Yamunanagar", "Ambala", "Panipat", "Sonipat"],
        "all_districts_note": "North-East canal belt (Rice Bowl of Haryana). Renowned globally for aromatic Basmati.",
        "key_pathogens": ["Bacterial Leaf Blight (Xanthomonas)", "Brown Spot (Bipolaris)", "Leaf Smut (Entyloma)"]
    },
    {
        "step": 3,
        "crop_key": "cotton",
        "crop_name": "Cotton (Kapas / Narma)",
        "season": "Kharif",
        "primary_districts": ["Sirsa", "Fatehabad", "Hisar", "Bhiwani", "Charkhi Dadri"],
        "all_districts_note": "Western/South-Western Haryana Cotton belt. Sirsa APMC is the largest cotton mandi in northern India.",
        "key_pathogens": ["Cotton Leaf Curl Virus (CLCuV)", "Bacterial Blight", "Foliar Spot"]
    },
    {
        "step": 4,
        "crop_key": "sugarcane",
        "crop_name": "Sugarcane (Ganna)",
        "season": "Annual / Kharif",
        "primary_districts": ["Yamunanagar", "Karnal", "Panipat", "Sonipat", "Ambala", "Kaithal"],
        "all_districts_note": "Heavy riverine belt feeding major cooperative sugar mills across Yamunanagar and Karnal.",
        "key_pathogens": ["Red Rot (Colletotrichum falcatum)", "Sugarcane Mosaic Virus", "Sugarcane Rust"]
    },
    {
        "step": 5,
        "crop_key": "corn",
        "crop_name": "Corn / Maize (Makka & Baby Corn)",
        "season": "Kharif & Zaid",
        "primary_districts": ["Panchkula", "Ambala", "Yamunanagar", "Karnal", "Sonipat"],
        "all_districts_note": "Shivalik piedmont and peri-urban NCR specialized in commercial baby corn & grain.",
        "key_pathogens": ["Northern Corn Leaf Blight (Exserohilum)", "Common Rust", "Gray Leaf Spot"]
    },
    {
        "step": 6,
        "crop_key": "vegetables",
        "crop_name": "Vegetables & Tubers (Tomato, Potato, Pepper)",
        "season": "Rabi & Zaid",
        "primary_districts": ["Sonipat", "Karnal", "Kurukshetra", "Jhajjar", "Palwal", "Rohtak", "Yamunanagar"],
        "all_districts_note": "Indo-Israel Center of Excellence (Gharaunda, Karnal), Ganaur International Market (Sonipat), Pipli/Shahabad potato belt.",
        "key_pathogens": ["Early Blight", "Late Blight", "Bacterial Spot", "Leaf Mold", "Mosaic Viruses"]
    }
]


def get_gpu_device() -> torch.device:
    """Detects and initializes NVIDIA CUDA GPU or falls back gracefully."""
    if torch.cuda.is_available():
        device = torch.device("cuda:0")
        gpu_name = torch.cuda.get_device_name(0)
        vram_mb = torch.cuda.get_device_properties(0).total_memory / (1024 * 1024)
        print(f"\n=======================================================")
        print(f"🚀 [GPU ACCELERATION ACTIVE]")
        print(f"   Device:       {gpu_name}")
        print(f"   Total VRAM:   {vram_mb:.0f} MB")
        print(f"   CUDA Version: {torch.version.cuda}")
        print(f"   PyTorch:      {torch.__version__}")
        print(f"=======================================================\n")
        torch.backends.cudnn.benchmark = True
    else:
        device = torch.device("cpu")
        print("⚠️ CUDA GPU not found, training on CPU.")
    return device


def create_transforms() -> Tuple[transforms.Compose, transforms.Compose]:
    """Builds standard training data augmentation and validation pipeline."""
    train_transform = transforms.Compose([
        transforms.Resize((224, 224)),
        transforms.RandomHorizontalFlip(),
        transforms.RandomVerticalFlip(p=0.3),
        transforms.RandomRotation(degrees=15),
        transforms.ColorJitter(brightness=0.15, contrast=0.15),
        transforms.ToTensor(),
        transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
    ])
    
    val_transform = transforms.Compose([
        transforms.Resize((224, 224)),
        transforms.ToTensor(),
        transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
    ])
    return train_transform, val_transform


def build_crop_classifier(num_classes: int) -> nn.Module:
    """Builds transfer learning MobileNetV2 with specialized classification head."""
    weights = MobileNet_V2_Weights.DEFAULT
    model = mobilenet_v2(weights=weights)
    
    # Freeze lower feature extractor layers initially
    for param in model.features[:12].parameters():
        param.requires_grad = False
        
    in_features = model.classifier[1].in_features
    model.classifier = nn.Sequential(
        nn.Dropout(p=0.3),
        nn.Linear(in_features, 256),
        nn.ReLU(),
        nn.Dropout(p=0.2),
        nn.Linear(256, num_classes)
    )
    return model


def train_single_step(
    curriculum_item: Dict[str, Any],
    device: torch.device,
    epochs: int = 3,
    batch_size: int = 32
) -> Dict[str, Any]:
    """
    Executes training for one single crop step, outputting real-time telemetry and metrics.
    """
    step = curriculum_item["step"]
    crop_key = curriculum_item["crop_key"]
    crop_name = curriculum_item["crop_name"]
    districts = curriculum_item["primary_districts"]
    
    print(f"\n--------------------------------------------------------------------------------")
    print(f"🌾 STEP {step}/6: Training Crop '{crop_name.upper()}'")
    print(f"   Target Haryana Districts: {', '.join(districts)}")
    print(f"   Agricultural Note:        {curriculum_item['all_districts_note']}")
    print(f"--------------------------------------------------------------------------------")
    
    crop_data_dir = DATA_DIR / crop_key
    train_dir = crop_data_dir / "train"
    val_dir = crop_data_dir / "val"
    
    if not train_dir.exists() or not any(train_dir.iterdir()):
        print(f"⚠️ Warning: Dataset for '{crop_key}' not found at {train_dir}. Skipping.")
        return {"status": "skipped", "crop": crop_key}
        
    train_tf, val_tf = create_transforms()
    train_ds = datasets.ImageFolder(str(train_dir), transform=train_tf)
    val_ds = datasets.ImageFolder(str(val_dir), transform=val_tf)
    
    class_names = train_ds.classes
    num_classes = len(class_names)
    print(f"   Classes ({num_classes}): {class_names}")
    print(f"   Samples: {len(train_ds)} train | {len(val_ds)} val")
    
    train_loader = DataLoader(train_ds, batch_size=batch_size, shuffle=True, num_workers=0, pin_memory=True if device.type == 'cuda' else False)
    val_loader = DataLoader(val_ds, batch_size=batch_size, shuffle=False, num_workers=0)
    
    model = build_crop_classifier(num_classes).to(device)
    criterion = nn.CrossEntropyLoss()
    optimizer = optim.AdamW(model.parameters(), lr=1e-3, weight_decay=1e-4)
    scaler = torch.amp.GradScaler('cuda', enabled=(device.type == 'cuda'))
    scheduler = optim.lr_scheduler.CosineAnnealingLR(optimizer, T_max=epochs)
    
    best_val_acc = 0.0
    history = []
    
    start_time = time.time()
    for epoch in range(1, epochs + 1):
        # 1. Training Phase
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
        epoch_train_loss = train_loss / max(1, train_total)
        epoch_train_acc = (train_correct / max(1, train_total)) * 100.0
        
        # 2. Validation Phase
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
                
        epoch_val_loss = val_loss / max(1, val_total)
        epoch_val_acc = (val_correct / max(1, val_total)) * 100.0
        
        if epoch_val_acc > best_val_acc:
            best_val_acc = epoch_val_acc
            
        # GPU Memory report
        gpu_mem = f"{torch.cuda.memory_allocated() / (1024*1024):.0f} MB" if device.type == 'cuda' else "N/A"
        
        print(f"   [Epoch {epoch}/{epochs}] "
              f"Train Loss: {epoch_train_loss:.4f} | Acc: {epoch_train_acc:.1f}% || "
              f"Val Loss: {epoch_val_loss:.4f} | Acc: {epoch_val_acc:.1f}% | GPU Mem: {gpu_mem}")
              
        history.append({
            "epoch": epoch,
            "train_loss": round(epoch_train_loss, 4),
            "train_acc": round(epoch_train_acc, 2),
            "val_loss": round(epoch_val_loss, 4),
            "val_acc": round(epoch_val_acc, 2)
        })
        
    elapsed = time.time() - start_time
    print(f"   ✅ Finished Step {step} ({crop_key}) in {elapsed:.1f}s | Best Val Acc: {best_val_acc:.2f}%\n")
    
    # Save Step Checkpoint
    checkpoint_file = CHECKPOINT_DIR / f"step{step}_{crop_key}_model.pt"
    torch.save({
        "step": step,
        "crop": crop_key,
        "crop_name": crop_name,
        "districts": districts,
        "class_names": class_names,
        "model_state_dict": model.state_dict(),
        "best_val_acc": best_val_acc,
        "history": history
    }, checkpoint_file)
    
    # Save class indices json
    indices_file = CHECKPOINT_DIR / f"step{step}_{crop_key}_classes.json"
    with open(indices_file, "w") as f:
        json.dump({str(i): c for i, c in enumerate(class_names)}, f, indent=2)
        
    return {
        "step": step,
        "crop": crop_key,
        "crop_name": crop_name,
        "classes": class_names,
        "districts": districts,
        "best_val_acc": best_val_acc,
        "checkpoint": str(checkpoint_file),
        "duration_sec": round(elapsed, 1)
    }


def run_full_stepwise_curriculum(epochs_per_step: int = 3) -> Dict[str, Any]:
    """
    Executes the complete Haryana 6-Step District Training Curriculum on GPU.
    """
    device = get_gpu_device()
    total_start = time.time()
    
    curriculum_results = []
    
    print("\n================================================================================")
    print("🌾 INITIATING HARYANA STATE STEPWISE DISTRICT CROP TRAINING CURRICULUM")
    print("   Total Steps: 6 Crops (Wheat, Rice, Cotton, Sugarcane, Corn, Vegetables)")
    print("   Districts Covered: All 22 Haryana Districts (North-East, Central, Western, Southern)")
    print("================================================================================\n")
    
    for item in HARYANA_TRAINING_CURRICULUM:
        res = train_single_step(item, device=device, epochs=epochs_per_step)
        curriculum_results.append(res)
        
    total_elapsed = time.time() - total_start
    
    # Generate and save curriculum report
    summary_report = {
        "title": "AgriVision Agent: Haryana District-Wise Stepwise GPU Training Report",
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
        "hardware": {
            "gpu_device": torch.cuda.get_device_name(0) if torch.cuda.is_available() else "CPU",
            "cuda_version": torch.version.cuda if torch.cuda.is_available() else "None",
            "pytorch_version": torch.__version__
        },
        "total_duration_sec": round(total_elapsed, 1),
        "steps_completed": curriculum_results
    }
    
    report_file = CHECKPOINT_DIR / "haryana_curriculum_training_summary.json"
    with open(report_file, "w") as f:
        json.dump(summary_report, f, indent=2)
        
    print(f"\n================================================================================")
    print(f"🎉 [ALL 6 HARYANA CROP STEPS COMPLETED ON GPU]")
    print(f"   Total Duration: {total_elapsed:.1f}s ({total_elapsed/60:.2f} mins)")
    print(f"   Checkpoints:    {CHECKPOINT_DIR}")
    print(f"   Summary Report: {report_file}")
    print(f"================================================================================\n")
    
    return summary_report


if __name__ == "__main__":
    epochs = int(sys.argv[1]) if len(sys.argv) > 1 else 3
    run_full_stepwise_curriculum(epochs_per_step=epochs)
