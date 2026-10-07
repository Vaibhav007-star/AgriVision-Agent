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


def validate_leaf_image(
    image: Image.Image,
    min_foliage_ratio: float = 10.0,
    min_texture_var: float = 8.0,
    skin_threshold_ratio: float = 12.0
) -> Dict[str, Any]:
    """
    Botanical & Out-of-Distribution (OOD) Guardrail:
    Validates whether the input photograph contains genuine agricultural crop leaf foliage.
    Detects and rejects non-plant objects, human faces/skin, animals, and blank backgrounds.
    
    Returns:
        Dict with keys:
            - is_leaf: bool (True if valid crop leaf, False if rejected)
            - reason: str ('valid_leaf', 'human_or_skin_detected', 'non_plant_object', 'blank_or_uniform_surface')
            - foliage_percentage: float (percentage of plant foliage pixels)
            - skin_percentage: float (percentage of human skin pixels)
            - mean_gli: float (Green Leaf Index)
            - texture_variance: float (Laplacian edge texture)
            - message: str (English user explanation)
            - message_hi: str (Hindi user explanation)
    """
    img_np = np.array(image.convert("RGB"))
    h_orig, w_orig = img_np.shape[:2]
    total_pixels = max(1, h_orig * w_orig)
    
    r = img_np[:, :, 0].astype(float)
    g = img_np[:, :, 1].astype(float)
    b = img_np[:, :, 2].astype(float)
    
    # 1. Texture Check (Laplacian Variance): Detect blank walls, solid colors, digital icons
    gray = cv2.cvtColor(img_np, cv2.COLOR_RGB2GRAY)
    texture_var = float(cv2.Laplacian(gray, cv2.CV_64F).var())
    if texture_var < min_texture_var:
        return {
            "is_leaf": False,
            "reason": "blank_or_uniform_surface",
            "foliage_percentage": 0.0,
            "skin_percentage": 0.0,
            "mean_gli": 0.0,
            "texture_variance": round(texture_var, 2),
            "message": "The uploaded image appears to be a blank or uniform surface without leaf biological texture.",
            "message_hi": "अपलोड की गई तस्वीर एक सादी सतह है जिसमें पौधे की पत्ती की कोई जैविक बनावट नहीं है।"
        }
        
    # 2. Human Skin Chrominance & Color Detection (YCbCr + HSV + RGB)
    y = 0.299 * r + 0.587 * g + 0.114 * b
    cr = (r - y) * 0.713 + 128
    cb = (b - y) * 0.564 + 128
    hsv = cv2.cvtColor(img_np, cv2.COLOR_RGB2HSV)
    h = hsv[:, :, 0]
    s = hsv[:, :, 1]
    v = hsv[:, :, 2]
    
    skin_mask = (
        (r > 75) & (g > 35) & (b > 18) &
        (r > g) & (r > b) & ((r - g) >= 8) &
        (cr >= 130) & (cr <= 178) & (cb >= 75) & (cb <= 130) &
        (((h <= 18) | (h >= 168)) & (s >= 20) & (s <= 200) & (v >= 45))
    )
    skin_pct = float(np.sum(skin_mask) / total_pixels * 100)
    
    # 3. Botanical Plant Foliage Detection (Green, Lime, Yellow-Green, Chlorotic/Blighted Tissue)
    green_foliage = (h >= 24) & (h <= 98) & (s >= 18) & (v >= 20)
    chlorosis_spots = (h >= 19) & (h < 24) & (s >= 20) & (v >= 25) & (g >= b)
    green_dom = (g > r * 0.88) & (g > b * 1.02) & (g > 30)
    
    foliage_mask = green_foliage | chlorosis_spots | green_dom
    foliage_pct = float(np.sum(foliage_mask) / total_pixels * 100)
    
    # 4. Green Leaf Index (GLI)
    denom = 2 * g + r + b
    denom[denom == 0] = 1e-5
    gli = (2 * g - r - b) / denom
    mean_gli = float(np.mean(gli))
    
    # Rule A: Human skin dominant over foliage
    if skin_pct > skin_threshold_ratio and skin_pct > foliage_pct * 0.5:
        return {
            "is_leaf": False,
            "reason": "human_or_skin_detected",
            "foliage_percentage": round(foliage_pct, 1),
            "skin_percentage": round(skin_pct, 1),
            "mean_gli": round(mean_gli, 3),
            "texture_variance": round(texture_var, 2),
            "message": "Human subject detected. AgriVision Agent is designed strictly for agricultural crop leaf pathology, not human diagnostics. No crop disease or pesticide treatment will be prescribed.",
            "message_hi": "मानव चेहरा या त्वचा पहचानी गई है। एग्रीविज़न एजेंट केवल फसलों (टमाटर, आलू, मिर्च, सेब आदि) की पत्तियों के रोग निदान के लिए बनाया गया है। किसी गैर-पौधे के लिए कोई कीटनाशक उपचार नहीं दिया जाएगा।"
        }
        
    # Rule B: Insufficient botanical foliage coverage (cars, furniture, animals, rooms, blue objects)
    if foliage_pct < min_foliage_ratio or (foliage_pct < 18.0 and mean_gli < -0.05):
        return {
            "is_leaf": False,
            "reason": "non_plant_object",
            "foliage_percentage": round(foliage_pct, 1),
            "skin_percentage": round(skin_pct, 1),
            "mean_gli": round(mean_gli, 3),
            "texture_variance": round(texture_var, 2),
            "message": "No crop leaf detected (insufficient plant foliage in image). Please upload a clear close-up photograph of an affected crop leaf to receive diagnosis and treatment.",
            "message_hi": "पौधे की पत्ती नहीं पाई गई (छवि में पत्तों का क्षेत्र बहुत कम है)। कृपया सही रोग निदान और उपचार के लिए पौधे की पत्ती की स्पष्ट तस्वीर अपलोड करें।"
        }
        
    return {
        "is_leaf": True,
        "reason": "valid_leaf",
        "foliage_percentage": round(foliage_pct, 1),
        "skin_percentage": round(skin_pct, 1),
        "mean_gli": round(mean_gli, 3),
        "texture_variance": round(texture_var, 2),
        "message": "Valid crop leaf foliage successfully detected.",
        "message_hi": "पौधे की पत्ती सफलतापूर्वक पहचानी गई।"
    }

