"""
Computer Vision & Image Preprocessing Pipeline for AgriVision Agent.
Handles image loading, normalization, visual enhancement (CLAHE),
leaf segmentation, and feature extraction.
"""

from typing import Tuple, Dict, Any, Union
from pathlib import Path
import io
import numpy as np
from PIL import Image, ImageEnhance
import cv2


def load_and_validate_image(image_source: Union[str, Path, bytes, io.BytesIO, Image.Image]) -> Image.Image:
    """
    Loads and validates an image from multiple possible source types.
    Converts to RGB format and verifies dimensional integrity.
    """
    if isinstance(image_source, Image.Image):
        image = image_source
    elif isinstance(image_source, (str, Path)):
        path = Path(image_source)
        if not path.exists():
            raise FileNotFoundError(f"Image not found at path: {path}")
        image = Image.open(path)
    elif isinstance(image_source, (bytes, bytearray)):
        image = Image.open(io.BytesIO(image_source))
    elif isinstance(image_source, io.BytesIO):
        image = Image.open(image_source)
    else:
        raise ValueError(f"Unsupported image source type: {type(image_source)}")
        
    # Ensure RGB color mode
    if image.mode != "RGB":
        image = image.convert("RGB")
        
    # Validation check: minimum dimensions
    w, h = image.size
    if w < 32 or h < 32:
        raise ValueError(f"Image dimensions too small ({w}x{h}). Minimum required is 32x32.")
        
    return image


def preprocess_for_model(
    image: Image.Image,
    target_size: Tuple[int, int] = (224, 224),
    normalization: str = "mobilenet"
) -> np.ndarray:
    """
    Prepares a PIL Image for Deep Learning (CNN) inference.
    Resizes using high-quality Lanczos resampling and scales values.
    
    Args:
        image: PIL Image in RGB format
        target_size: Tuple of (height, width) e.g., (224, 224)
        normalization: 'mobilenet' (scaled to [-1, 1]) or 'standard' (scaled to [0, 1])
        
    Returns:
        np.ndarray with shape (1, height, width, 3), dtype float32
    """
    # Resize image
    resized_img = image.resize(target_size, Image.Resampling.LANCZOS)
    
    # Convert to float numpy array
    img_array = np.array(resized_img, dtype=np.float32)
    
    # Normalize
    if normalization == "mobilenet":
        # Scale to [-1, 1] as standard in MobileNetV2
        img_array = (img_array / 127.5) - 1.0
    elif normalization == "standard":
        # Scale to [0, 1]
        img_array = img_array / 255.0
    else:
        img_array = img_array / 255.0
        
    # Add batch dimension (1, H, W, C)
    return np.expand_dims(img_array, axis=0)


def apply_clahe_enhancement(image: Image.Image) -> Image.Image:
    """
    Applies Contrast Limited Adaptive Histogram Equalization (CLAHE) on the L channel (LAB color space).
    Enhances subtle leaf lesion textures, spot boundaries, and discoloration.
    """
    # Convert PIL Image to OpenCV BGR
    img_np = np.array(image)
    lab = cv2.cvtColor(img_np, cv2.COLOR_RGB2LAB)
    l_channel, a_channel, b_channel = cv2.split(lab)
    
    # Apply CLAHE to L channel
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
    cl = clahe.apply(l_channel)
    
    # Merge and convert back to RGB
    limg = cv2.merge((cl, a_channel, b_channel))
    enhanced_rgb = cv2.cvtColor(limg, cv2.COLOR_LAB2RGB)
    
    return Image.fromarray(enhanced_rgb)


def segment_leaf_mask(image: Image.Image) -> Dict[str, Any]:
    """
    Segments the leaf from background using color thresholding in HSV space.
    Calculates estimated green leaf area vs. necrotic/lesion spot area.
    
    Returns:
        Dict containing mask Image, lesion_percentage, and segmented_leaf Image.
    """
    img_np = np.array(image)
    hsv = cv2.cvtColor(img_np, cv2.COLOR_RGB2HSV)
    
    # Plant foliage mask (broad green/yellow/brown range)
    lower_plant = np.array([15, 25, 25])
    upper_plant = np.array([100, 255, 255])
    plant_mask = cv2.inRange(hsv, lower_plant, upper_plant)
    
    # Healthy green mask
    lower_green = np.array([35, 40, 40])
    upper_green = np.array([85, 255, 255])
    green_mask = cv2.inRange(hsv, lower_green, upper_green)
    
    # Lesion / Diseased / Necrotic spot mask (Brown/Yellow/Dark spots within leaf)
    lower_lesion = np.array([10, 50, 20])
    upper_lesion = np.array([30, 255, 220])
    lesion_mask = cv2.inRange(hsv, lower_lesion, upper_lesion)
    
    total_plant_pixels = max(1, cv2.countNonZero(plant_mask))
    lesion_pixels = cv2.countNonZero(lesion_mask)
    
    # Estimate lesion damage ratio
    damage_ratio = min(100.0, round((lesion_pixels / total_plant_pixels) * 100, 1))
    
    # Masked leaf image on white background
    segmented = cv2.bitwise_and(img_np, img_np, mask=plant_mask)
    white_bg = np.full_like(img_np, 255)
    mask_inv = cv2.bitwise_not(plant_mask)
    background = cv2.bitwise_and(white_bg, white_bg, mask=mask_inv)
    final_segmented = cv2.add(segmented, background)
    
    return {
        "mask_image": Image.fromarray(plant_mask),
        "segmented_image": Image.fromarray(final_segmented),
        "lesion_percentage": damage_ratio,
        "total_plant_pixels": total_plant_pixels
    }


def extract_leaf_features(image: Image.Image) -> Dict[str, float]:
    """
    Calculates numerical agronomic vision indices from image:
    - GLI (Green Leaf Index): (2*G - R - B) / (2*G + R + B)
    - VARI (Visible Atmospherically Resistant Index): (G - R) / (G + R - B)
    - Mean RGB brightness levels
    """
    img_np = np.array(image, dtype=np.float32)
    r = img_np[:, :, 0]
    g = img_np[:, :, 1]
    b = img_np[:, :, 2]
    
    denom_gli = 2 * g + r + b
    denom_gli[denom_gli == 0] = 1e-6
    gli = (2 * g - r - b) / denom_gli
    
    denom_vari = g + r - b
    denom_vari[denom_vari == 0] = 1e-6
    vari = (g - r) / denom_vari
    
    return {
        "mean_green_leaf_index": float(np.mean(gli)),
        "mean_vari_index": float(np.mean(vari)),
        "mean_red": float(np.mean(r)),
        "mean_green": float(np.mean(g)),
        "mean_blue": float(np.mean(b))
    }


def generate_gradcam_overlay(original_image: Image.Image, heatmap_2d: np.ndarray, alpha: float = 0.45) -> Image.Image:
    """
    Generates a colorized Grad-CAM explainability heatmap overlay on top of the original leaf image.
    Helps visualize which leaf lesions influenced the CNN classification.
    """
    img_np = np.array(original_image)
    h, w = img_np.shape[:2]
    
    # Normalize heatmap between 0 and 255
    heatmap_norm = np.uint8(255 * (heatmap_2d - np.min(heatmap_2d)) / (np.max(heatmap_2d) - np.min(heatmap_2d) + 1e-8))
    heatmap_resized = cv2.resize(heatmap_norm, (w, h))
    
    # Apply JET colormap
    heatmap_color = cv2.applyColorMap(heatmap_resized, cv2.COLORMAP_JET)
    heatmap_color_rgb = cv2.cvtColor(heatmap_color, cv2.COLOR_BGR2RGB)
    
    # Superimpose heatmap onto original image
    superimposed = np.uint8(img_np * (1 - alpha) + heatmap_color_rgb * alpha)
    return Image.fromarray(superimposed)

