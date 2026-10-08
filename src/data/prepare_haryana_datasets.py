"""
Haryana Agricultural Dataset Preprocessor & Curriculum Splitter (src/data/prepare_haryana_datasets.py).

Organizes all harvested Kaggle and benchmark crop datasets into a clean, standardized
crop-by-crop structure for stepwise GPU training:
- data/haryana_dataset_curriculum/{crop}/train/{class_name}/
- data/haryana_dataset_curriculum/{crop}/val/{class_name}/

Supports:
1. Wheat (Leaf Rust, Stem Rust, Stripe Rust, Healthy)
2. Rice (Bacterial Blight, Brown Spot, Leaf Smut)
3. Cotton (Diseased Leaf, Fresh Leaf, Diseased Plant, Fresh Plant)
4. Sugarcane (Red Rot, Mosaic, Rust, Yellow, Healthy)
5. Corn / Maize (Diseased, Healthy)
6. Vegetables & Tubers (Tomato, Potato, Pepper Bell from data/raw)
"""

import os
import shutil
import random
from pathlib import Path
from typing import Dict, List, Tuple

BASE_DIR = Path("c:/Projects/AgriVision Agent")
OUTPUT_BASE = BASE_DIR / "data" / "haryana_curriculum"


def prepare_wheat(val_split: float = 0.2):
    print("Preparing Wheat dataset...")
    src_dir = BASE_DIR / "data" / "haryana_crops" / "wheat"
    dest_train = OUTPUT_BASE / "wheat" / "train"
    dest_val = OUTPUT_BASE / "wheat" / "val"
    
    mapping = {
        "healthy": "Wheat___healthy",
        "leaf rust": "Wheat___leaf_rust",
        "stem rust": "Wheat___stem_rust",
        "stripe rust": "Wheat___stripe_rust"
    }
    
    for folder_name, class_name in mapping.items():
        src_folder = src_dir / folder_name
        if not src_folder.exists():
            continue
        images = [f for f in src_folder.iterdir() if f.is_file() and f.suffix.lower() in [".jpg", ".jpeg", ".png"]]
        random.seed(42)
        random.shuffle(images)
        
        split_idx = int(len(images) * (1 - val_split))
        train_imgs = images[:split_idx]
        val_imgs = images[split_idx:]
        
        (dest_train / class_name).mkdir(parents=True, exist_ok=True)
        (dest_val / class_name).mkdir(parents=True, exist_ok=True)
        
        for img in train_imgs:
            shutil.copy2(img, dest_train / class_name / img.name)
        for img in val_imgs:
            shutil.copy2(img, dest_val / class_name / img.name)
            
    print(f"  -> Wheat prepared at {OUTPUT_BASE / 'wheat'}")


def prepare_rice(val_split: float = 0.2):
    print("Preparing Rice dataset...")
    src_dir = BASE_DIR / "data" / "haryana_crops" / "rice" / "rice_leaf_diseases"
    dest_train = OUTPUT_BASE / "rice" / "train"
    dest_val = OUTPUT_BASE / "rice" / "val"
    
    mapping = {
        "Bacterial leaf blight": "Rice___bacterial_blight",
        "Brown spot": "Rice___brown_spot",
        "Leaf smut": "Rice___leaf_smut"
    }
    
    for folder_name, class_name in mapping.items():
        src_folder = src_dir / folder_name
        if not src_folder.exists():
            continue
        images = [f for f in src_folder.iterdir() if f.is_file() and f.suffix.lower() in [".jpg", ".jpeg", ".png"]]
        random.seed(42)
        random.shuffle(images)
        
        split_idx = int(len(images) * (1 - val_split))
        train_imgs = images[:split_idx]
        val_imgs = images[split_idx:]
        
        (dest_train / class_name).mkdir(parents=True, exist_ok=True)
        (dest_val / class_name).mkdir(parents=True, exist_ok=True)
        
        for img in train_imgs:
            shutil.copy2(img, dest_train / class_name / img.name)
        for img in val_imgs:
            shutil.copy2(img, dest_val / class_name / img.name)
            
    print(f"  -> Rice prepared at {OUTPUT_BASE / 'rice'}")


def prepare_cotton(val_split: float = 0.2):
    print("Preparing Cotton dataset...")
    src_dir = BASE_DIR / "data" / "haryana_crops" / "cotton" / "Cotton Disease"
    dest_train = OUTPUT_BASE / "cotton" / "train"
    dest_val = OUTPUT_BASE / "cotton" / "val"
    
    mapping = {
        "diseased cotton leaf": "Cotton___diseased_leaf",
        "fresh cotton leaf": "Cotton___healthy_leaf",
        "diseased cotton plant": "Cotton___diseased_plant",
        "fresh cotton plant": "Cotton___healthy_plant"
    }
    
    for target_class, class_name in mapping.items():
        all_images = []
        for split in ["train", "val", "test"]:
            folder = src_dir / split / target_class
            if folder.exists():
                all_images.extend([f for f in folder.iterdir() if f.is_file() and f.suffix.lower() in [".jpg", ".jpeg", ".png"]])
                
        random.seed(42)
        random.shuffle(all_images)
        
        # Subsample if too large to balance training
        if len(all_images) > 400:
            all_images = all_images[:400]
            
        split_idx = int(len(all_images) * (1 - val_split))
        train_imgs = all_images[:split_idx]
        val_imgs = all_images[split_idx:]
        
        (dest_train / class_name).mkdir(parents=True, exist_ok=True)
        (dest_val / class_name).mkdir(parents=True, exist_ok=True)
        
        for img in train_imgs:
            shutil.copy2(img, dest_train / class_name / img.name)
        for img in val_imgs:
            shutil.copy2(img, dest_val / class_name / img.name)
            
    print(f"  -> Cotton prepared at {OUTPUT_BASE / 'cotton'}")


def prepare_sugarcane(val_split: float = 0.2):
    print("Preparing Sugarcane dataset...")
    src_dir = BASE_DIR / "data" / "haryana_crops" / "sugarcane"
    dest_train = OUTPUT_BASE / "sugarcane" / "train"
    dest_val = OUTPUT_BASE / "sugarcane" / "val"
    
    mapping = {
        "Healthy": "Sugarcane___healthy",
        "RedRot": "Sugarcane___red_rot",
        "Rust": "Sugarcane___rust",
        "Yellow": "Sugarcane___yellow_leaf",
        "Mosaic": "Sugarcane___mosaic"
    }
    
    for folder_name, class_name in mapping.items():
        src_folder = src_dir / folder_name
        if not src_folder.exists():
            continue
        images = [f for f in src_folder.iterdir() if f.is_file() and f.suffix.lower() in [".jpg", ".jpeg", ".png"]]
        random.seed(42)
        random.shuffle(images)
        
        if len(images) > 400:
            images = images[:400]
            
        split_idx = int(len(images) * (1 - val_split))
        train_imgs = images[:split_idx]
        val_imgs = images[split_idx:]
        
        (dest_train / class_name).mkdir(parents=True, exist_ok=True)
        (dest_val / class_name).mkdir(parents=True, exist_ok=True)
        
        for img in train_imgs:
            shutil.copy2(img, dest_train / class_name / img.name)
        for img in val_imgs:
            shutil.copy2(img, dest_val / class_name / img.name)
            
    print(f"  -> Sugarcane prepared at {OUTPUT_BASE / 'sugarcane'}")


def prepare_corn(val_split: float = 0.2):
    print("Preparing Corn/Maize dataset...")
    src_dir = BASE_DIR / "data" / "haryana_crops" / "corn" / "Corn Healthy and Disease"
    dest_train = OUTPUT_BASE / "corn" / "train"
    dest_val = OUTPUT_BASE / "corn" / "val"
    
    mapping = {
        "diseased": "Corn___blight_diseased",
        "healthy": "Corn___healthy"
    }
    
    for folder_name, class_name in mapping.items():
        src_folder = src_dir / folder_name
        if not src_folder.exists():
            continue
        images = [f for f in src_folder.iterdir() if f.is_file() and f.suffix.lower() in [".jpg", ".jpeg", ".png"]]
        random.seed(42)
        random.shuffle(images)
        
        if len(images) > 400:
            images = images[:400]
            
        split_idx = int(len(images) * (1 - val_split))
        train_imgs = images[:split_idx]
        val_imgs = images[split_idx:]
        
        (dest_train / class_name).mkdir(parents=True, exist_ok=True)
        (dest_val / class_name).mkdir(parents=True, exist_ok=True)
        
        for img in train_imgs:
            shutil.copy2(img, dest_train / class_name / img.name)
        for img in val_imgs:
            shutil.copy2(img, dest_val / class_name / img.name)
            
    print(f"  -> Corn prepared at {OUTPUT_BASE / 'corn'}")


def prepare_vegetables(val_split: float = 0.2, max_per_class: int = 150):
    print("Preparing Vegetables & Tubers (Tomato, Potato, Pepper) dataset...")
    src_dir = BASE_DIR / "data" / "raw"
    dest_train = OUTPUT_BASE / "vegetables" / "train"
    dest_val = OUTPUT_BASE / "vegetables" / "val"
    
    if not src_dir.exists():
        print("data/raw not found, skipping vegetables copy.")
        return
        
    for class_folder in src_dir.iterdir():
        if not class_folder.is_dir():
            continue
        class_name = class_folder.name
        images = [f for f in class_folder.iterdir() if f.is_file() and f.suffix.lower() in [".jpg", ".jpeg", ".png"]]
        random.seed(42)
        random.shuffle(images)
        
        images = images[:max_per_class]
        split_idx = int(len(images) * (1 - val_split))
        train_imgs = images[:split_idx]
        val_imgs = images[split_idx:]
        
        (dest_train / class_name).mkdir(parents=True, exist_ok=True)
        (dest_val / class_name).mkdir(parents=True, exist_ok=True)
        
        for img in train_imgs:
            shutil.copy2(img, dest_train / class_name / img.name)
        for img in val_imgs:
            shutil.copy2(img, dest_val / class_name / img.name)
            
    print(f"  -> Vegetables prepared at {OUTPUT_BASE / 'vegetables'}")


def run_all_preparation():
    print(f"Building Haryana Crop Curriculum Dataset in {OUTPUT_BASE}...")
    OUTPUT_BASE.mkdir(parents=True, exist_ok=True)
    prepare_wheat()
    prepare_rice()
    prepare_cotton()
    prepare_sugarcane()
    prepare_corn()
    prepare_vegetables()
    print("\nAll 6 Haryana crop curriculum groups organized successfully!")


if __name__ == "__main__":
    run_all_preparation()

