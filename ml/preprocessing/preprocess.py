"""
Image Preprocessing, Augmentation & Dataset Splitting Pipeline for AgriVision Agent.
Reads config.yaml, standardizes images to (224, 224), applies realistic augmentations,
and generates stratified Train / Val / Test partitions.
"""

from typing import Dict, Any, List, Tuple, Optional
import os
import sys
from pathlib import Path
import random
import json
import yaml
import numpy as np
from PIL import Image, ImageEnhance, ImageOps

# Ensure project root is in sys.path
BASE_DIR = Path(__file__).resolve().parent.parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))


def load_config(config_path: Optional[Path] = None) -> Dict[str, Any]:
    """Loads master configuration from config.yaml."""
    if config_path is None:
        config_path = BASE_DIR / "config.yaml"
    with open(config_path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def apply_realistic_augmentation(img: Image.Image, aug_config: Dict[str, Any]) -> Image.Image:
    """
    Applies realistic botanical image augmentations to a PIL Image:
    - Moderate rotation (e.g. +/- 20 degrees)
    - Horizontal flip (50% probability)
    - Slight zoom / crop (0.85 - 1.15x)
    - Natural brightness variations (mimicking cloud cover/daylight)
    """
    aug_img = img.copy()
    
    # 1. Horizontal Flip
    if aug_config.get("horizontal_flip", True) and random.random() > 0.5:
        aug_img = aug_img.transpose(Image.FLIP_LEFT_RIGHT)
        
    # 2. Moderate Rotation
    max_rot = aug_config.get("rotation_range_degrees", 20)
    angle = random.uniform(-max_rot, max_rot)
    aug_img = aug_img.rotate(angle, resample=Image.Resampling.BILINEAR, expand=False)
    
    # 3. Slight Zoom / Crop
    zoom_range = aug_config.get("zoom_range", [0.85, 1.15])
    zoom_factor = random.uniform(zoom_range[0], zoom_range[1])
    w, h = aug_img.size
    if zoom_factor != 1.0:
        new_w, new_h = int(w * zoom_factor), int(h * zoom_factor)
        resized = aug_img.resize((new_w, new_h), Image.Resampling.BILINEAR)
        # Crop or pad to original size
        if zoom_factor > 1.0:
            left = (new_w - w) // 2
            top = (new_h - h) // 2
            aug_img = resized.crop((left, top, left + w, top + h))
        else:
            padded = Image.new("RGB", (w, h), color=(235, 235, 235))
            left = (w - new_w) // 2
            top = (h - new_h) // 2
            padded.paste(resized, (left, top))
            aug_img = padded
            
    # 4. Brightness Variation (Daylight / Cloud simulation)
    bright_range = aug_config.get("brightness_range", [0.85, 1.15])
    bright_factor = random.uniform(bright_range[0], bright_range[1])
    enhancer = ImageEnhance.Brightness(aug_img)
    aug_img = enhancer.enhance(bright_factor)
    
    return aug_img


def process_image(img_path: Path, target_size: Tuple[int, int] = (224, 224)) -> Image.Image:
    """Loads image, converts to RGB mode, and resizes via Lanczos interpolation."""
    with Image.open(img_path) as img:
        if img.mode != "RGB":
            img = img.convert("RGB")
        return img.resize(target_size, Image.Resampling.LANCZOS)


if sys.stdout.encoding != 'utf-8':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass


def run_preprocessing_pipeline(config_path: Optional[Path] = None) -> Dict[str, Any]:
    """
    Executes end-to-end dataset preprocessing, splitting, and augmentation pipeline.
    """
    cfg = load_config(config_path)
    dataset_cfg = cfg["dataset"]
    
    raw_dir = BASE_DIR / dataset_cfg["raw_dir"]
    processed_dir = BASE_DIR / dataset_cfg["processed_dir"]
    target_size = tuple(dataset_cfg.get("image_size", [224, 224]))
    
    train_ratio = dataset_cfg.get("train_split", 0.70)
    val_ratio = dataset_cfg.get("val_split", 0.15)
    test_ratio = dataset_cfg.get("test_split", 0.15)
    seed = dataset_cfg.get("random_seed", 42)
    
    random.seed(seed)
    np.random.seed(seed)
    
    # Determine target classes
    if dataset_cfg.get("use_full_dataset", False):
        classes = sorted([d.name for d in raw_dir.iterdir() if d.is_dir()])
    else:
        classes = dataset_cfg.get("selected_classes", ["Tomato___Early_blight", "Tomato___Late_blight", "Tomato___healthy"])
        
    print("=" * 70)
    print("[AgriVision Agent] Image Preprocessing & Augmentation Pipeline")
    print("=" * 70)
    print(f"Input Raw Directory:       {raw_dir}")
    print(f"Output Processed Directory: {processed_dir}")
    print(f"Target Image Dimensions:   {target_size[0]}x{target_size[1]} px")
    print(f"Partitions Ratio:          Train={train_ratio*100:.0f}%, Val={val_ratio*100:.0f}%, Test={test_ratio*100:.0f}%")
    print(f"Classes ({len(classes)}):           {', '.join(classes)}")
    print("-" * 70)
    
    # Setup processed directories
    splits = ["train", "val", "test"]
    for s in splits:
        for c in classes:
            (processed_dir / s / c).mkdir(parents=True, exist_ok=True)
            
    summary_stats = {
        "num_classes": len(classes),
        "classes": classes,
        "splits": {"train": 0, "val": 0, "test": 0},
        "per_class": {}
    }
    
    class_indices = {}
    for idx, c in enumerate(classes):
        class_meta = {
            "index": idx,
            "class_name": c,
            "crop": c.split("___")[0].replace("_", " ").title() if "___" in c else c,
            "disease": c.split("___")[1].replace("_", " ").title() if "___" in c else "Unknown",
            "is_healthy": "healthy" in c.lower()
        }
        class_indices[str(idx)] = class_meta
        
    aug_cfg = dataset_cfg.get("augmentation", {})
    
    # Process each class
    for c in classes:
        class_folder = raw_dir / c
        if not class_folder.exists():
            print(f"[!] Warning: Folder not found for class: {c}")
            continue
            
        all_imgs = sorted(list(class_folder.glob("*.jpg")) + list(class_folder.glob("*.jpeg")) + list(class_folder.glob("*.png")))
        random.shuffle(all_imgs)
        
        n_total = len(all_imgs)
        if n_total == 0:
            print(f"[!] Warning: No images found in {class_folder}")
            continue
            
        n_train = max(1, int(n_total * train_ratio))
        n_val = max(1, int(n_total * val_ratio))
        
        train_files = all_imgs[:n_train]
        val_files = all_imgs[n_train:n_train + n_val]
        test_files = all_imgs[n_train + n_val:]
        
        # 1. Process Train files + Augmentations
        train_count = 0
        for f in train_files:
            img = process_image(f, target_size)
            # Save original standardized image
            dest_orig = processed_dir / "train" / c / f"{f.stem}_std.jpg"
            img.save(dest_orig, "JPEG", quality=95)
            train_count += 1
            
            # Generate 2 augmented copies per training sample
            for aug_i in range(1, 3):
                aug_img = apply_realistic_augmentation(img, aug_cfg)
                dest_aug = processed_dir / "train" / c / f"{f.stem}_aug{aug_i}.jpg"
                aug_img.save(dest_aug, "JPEG", quality=95)
                train_count += 1
                
        # 2. Process Validation files (un-augmented)
        val_count = 0
        for f in val_files:
            img = process_image(f, target_size)
            dest = processed_dir / "val" / c / f"{f.name}"
            img.save(dest, "JPEG", quality=95)
            val_count += 1
            
        # 3. Process Test files (un-augmented)
        test_count = 0
        for f in test_files:
            img = process_image(f, target_size)
            dest = processed_dir / "test" / c / f"{f.name}"
            img.save(dest, "JPEG", quality=95)
            test_count += 1
            
        summary_stats["per_class"][c] = {
            "raw_total": n_total,
            "train_processed_augmented": train_count,
            "val_processed": val_count,
            "test_processed": test_count
        }
        summary_stats["splits"]["train"] += train_count
        summary_stats["splits"]["val"] += val_count
        summary_stats["splits"]["test"] += test_count
        
        print(f"  [+] {c}: {n_total} raw -> {train_count} train (aug) | {val_count} val | {test_count} test")
        
    # Save Metadata
    summary_path = processed_dir / "dataset_summary.json"
    with open(summary_path, "w", encoding="utf-8") as f:
        json.dump(summary_stats, f, indent=2)
        
    indices_path = processed_dir / "class_indices.json"
    with open(indices_path, "w", encoding="utf-8") as f:
        json.dump(class_indices, f, indent=2)
        
    print("-" * 70)
    print("[Preprocessing Complete Summary]")
    print(f"Total Processed Train Samples (with Augmentation): {summary_stats['splits']['train']}")
    print(f"Total Validation Samples:                           {summary_stats['splits']['val']}")
    print(f"Total Test Samples:                                 {summary_stats['splits']['test']}")
    print(f"Summary JSON saved to:                              {summary_path}")
    print("=" * 70)
    
    return summary_stats


if __name__ == "__main__":
    run_preprocessing_pipeline()
