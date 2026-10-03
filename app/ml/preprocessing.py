"""
Image Preprocessing, CLAHE Enhancement & Normalization Module (app/ml/preprocessing.py).
"""

from typing import Tuple, Dict, Any, Union
from pathlib import Path
import numpy as np
import cv2
from PIL import Image, ImageOps


def load_and_validate_image(
    image_input: Union[str, Path, Image.Image, np.ndarray],
    min_size: Tuple[int, int] = (32, 32)
) -> Image.Image:
    """Loads and verifies that input image is valid RGB."""
    if isinstance(image_input, (str, Path)):
        if not Path(image_input).exists():
            raise FileNotFoundError(f"Image not found at path: {image_input}")
        img = Image.open(str(image_input))
    elif isinstance(image_input, Image.Image):
        img = image_input
    elif isinstance(image_input, np.ndarray):
        img = Image.fromarray(image_input.astype("uint8"))
    else:
        raise ValueError(f"Unsupported image input type: {type(image_input)}")
        
    if img.mode != "RGB":
        img = img.convert("RGB")
        
    w, h = img.size
    if w < min_size[0] or h < min_size[1]:
        raise ValueError(f"Image dimensions ({w}x{h}) are smaller than minimum allowed ({min_size[0]}x{min_size[1]}).")
        
    return img


def apply_clahe(img: Image.Image, clip_limit: float = 2.0, grid_size: Tuple[int, int] = (8, 8)) -> Image.Image:
    """Applies Contrast Limited Adaptive Histogram Equalization in LAB color space."""
    img_np = np.array(img)
    lab = cv2.cvtColor(img_np, cv2.COLOR_RGB2LAB)
    l_channel, a_channel, b_channel = cv2.split(lab)
    
    clahe = cv2.createCLAHE(clipLimit=clip_limit, tileGridSize=grid_size)
    cl = clahe.apply(l_channel)
    
    merged_lab = cv2.merge((cl, a_channel, b_channel))
    enhanced_rgb = cv2.cvtColor(merged_lab, cv2.COLOR_LAB2RGB)
    return Image.fromarray(enhanced_rgb)


def preprocess_for_inference(
    img: Image.Image,
    target_size: Tuple[int, int] = (224, 224)
) -> Tuple[np.ndarray, Image.Image]:
    """Resizes and normalizes image to [-1.0, 1.0] for MobileNetV2."""
    resized = img.resize(target_size, Image.Resampling.LANCZOS)
    arr = np.array(resized, dtype=np.float32)
    norm_tensor = (arr / 127.5) - 1.0
    batch_tensor = np.expand_dims(norm_tensor, axis=0)
    return batch_tensor, resized

