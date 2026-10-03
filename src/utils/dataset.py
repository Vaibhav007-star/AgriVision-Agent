"""
Dataset Management & Sample Image Generator for AgriVision Agent.
Provides dataset loader helpers, augmentation pipelines, and generates
realistic synthetic/sample images for all major crop disease classes.
"""

from typing import List, Dict, Tuple, Optional, Any
import os
import json
from pathlib import Path
import numpy as np
from PIL import Image, ImageDraw, ImageFilter
from src.config import config


def generate_benchmark_sample_images() -> List[str]:
    """
    Generates realistic sample leaf benchmark images with realistic visual lesions
    for instant local evaluation without requiring immediate gigabytes of downloads.
    Saves to data/sample_images/ and returns the list of filepaths.
    """
    sample_dir = Path(config.base_dir) / "data" / "sample_images"
    sample_dir.mkdir(parents=True, exist_ok=True)
    
    samples = [
        {"filename": "tomato_early_blight.jpg", "crop": "Tomato", "disease": "Early Blight", "bg_color": (34, 139, 34), "spots": True, "spot_color": (101, 67, 33), "halo": True},
        {"filename": "tomato_late_blight.jpg", "crop": "Tomato", "disease": "Late Blight", "bg_color": (46, 117, 46), "spots": True, "spot_color": (40, 40, 40), "water_soaked": True},
        {"filename": "tomato_healthy.jpg", "crop": "Tomato", "disease": "Healthy", "bg_color": (50, 168, 82), "spots": False},
        {"filename": "potato_early_blight.jpg", "crop": "Potato", "disease": "Early Blight", "bg_color": (60, 140, 50), "spots": True, "spot_color": (87, 59, 12), "concentric": True},
        {"filename": "potato_late_blight.jpg", "crop": "Potato", "disease": "Late Blight", "bg_color": (45, 120, 45), "spots": True, "spot_color": (54, 43, 31)},
        {"filename": "potato_healthy.jpg", "crop": "Potato", "disease": "Healthy", "bg_color": (58, 175, 75), "spots": False},
        {"filename": "corn_common_rust.jpg", "crop": "Corn (Maize)", "disease": "Common Rust", "bg_color": (120, 175, 60), "spots": True, "spot_color": (184, 90, 20), "elongated": True},
        {"filename": "corn_healthy.jpg", "crop": "Corn (Maize)", "disease": "Healthy", "bg_color": (70, 180, 50), "spots": False},
        {"filename": "apple_scab.jpg", "crop": "Apple", "disease": "Apple Scab", "bg_color": (50, 150, 60), "spots": True, "spot_color": (45, 65, 30), "velvety": True},
        {"filename": "apple_healthy.jpg", "crop": "Apple", "disease": "Healthy", "bg_color": (65, 185, 70), "spots": False},
        {"filename": "pepper_bacterial_spot.jpg", "crop": "Pepper Bell", "disease": "Bacterial Spot", "bg_color": (40, 145, 50), "spots": True, "spot_color": (30, 30, 30), "small_angular": True}
    ]
    
    generated_paths = []
    
    for s in samples:
        file_path = sample_dir / s["filename"]
        if not file_path.exists():
            # Create a synthetic leaf canvas (300 x 300)
            img = Image.new("RGB", (300, 300), color=(240, 240, 240)) # neutral gray background
            draw = ImageDraw.Draw(img)
            
            # Draw leaf elliptical shape with base green color
            leaf_box = [40, 30, 260, 270]
            draw.ellipse(leaf_box, fill=s["bg_color"], outline=(20, 90, 20), width=2)
            
            # Draw leaf main vein and lateral veins
            draw.line([(150, 30), (150, 270)], fill=(180, 220, 140), width=3)
            for y_pos in range(70, 240, 30):
                draw.line([(150, y_pos), (80, y_pos - 20)], fill=(160, 210, 130), width=2)
                draw.line([(150, y_pos), (220, y_pos - 20)], fill=(160, 210, 130), width=2)
                
            # If diseased, draw characteristic lesion spots
            if s.get("spots", False):
                spot_color = s["spot_color"]
                
                # Draw main lesion spots
                if s.get("concentric", False) or s.get("halo", False):
                    # Concentric rings (Early Blight characteristic target-board spots)
                    for r_offset in [(95, 110, 15), (190, 160, 18), (140, 200, 12)]:
                        x, y, rad = r_offset
                        draw.ellipse([x-rad-5, y-rad-5, x+rad+5, y+rad+5], fill=(210, 190, 80)) # yellow halo
                        draw.ellipse([x-rad, y-rad, x+rad, y+rad], fill=spot_color) # brown center
                        draw.ellipse([x-rad+4, y-rad+4, x+rad-4, y+rad-4], fill=(50, 30, 10))
                elif s.get("elongated", False):
                    # Rust pustules
                    for (x, y) in [(110, 90), (130, 130), (170, 100), (160, 180), (120, 220), (180, 150)]:
                        draw.ellipse([x-8, y-4, x+8, y+4], fill=spot_color)
                elif s.get("small_angular", False):
                    # Bacterial spots (small angular dark spots)
                    for (x, y) in [(100, 80), (115, 120), (180, 110), (160, 160), (130, 190), (170, 210), (90, 160)]:
                        draw.rectangle([x-4, y-4, x+4, y+4], fill=spot_color)
                else:
                    # Generic / late blight water-soaked spots
                    for (x, y, r) in [(110, 100, 22), (180, 150, 28), (135, 190, 18)]:
                        draw.ellipse([x-r, y-r, x+r, y+r], fill=spot_color)
                        
            # Apply slight Gaussian blur for natural gradient transitions
            img = img.filter(ImageFilter.GaussianBlur(radius=0.7))
            
            # Save file
            img.save(file_path, quality=92)
            
        generated_paths.append(str(file_path))
        
    return generated_paths


def get_available_samples() -> Dict[str, str]:
    """Returns mapping of sample description to image file paths."""
    generate_benchmark_sample_images()
    sample_dir = Path(config.base_dir) / "data" / "sample_images"
    
    mapping = {}
    if sample_dir.exists():
        for img_file in sample_dir.glob("*.jpg"):
            name = img_file.stem.replace("_", " ").title()
            mapping[name] = str(img_file)
    return mapping


def load_class_indices() -> Dict[int, Dict[str, Any]]:
    """Loads the class indices dictionary."""
    indices_path = Path(config.model.CLASS_INDICES_PATH)
    if indices_path.exists():
        with open(indices_path, "r", encoding="utf-8") as f:
            data = json.load(f)
            return {int(k): v for k, v in data.items()}
    return {}
