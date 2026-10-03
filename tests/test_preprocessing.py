"""
Unit tests for Image Preprocessing, CLAHE, and Augmentation (tests/test_preprocessing.py).
"""

import unittest
from pathlib import Path
import numpy as np
from PIL import Image

from app.ml.preprocessing import load_and_validate_image, apply_clahe, preprocess_for_inference
from src.utils.image_processing import segment_leaf_mask


class TestPreprocessing(unittest.TestCase):
    
    def setUp(self):
        self.base_dir = Path(__file__).resolve().parent.parent
        self.sample_img_path = self.base_dir / "data" / "sample_images" / "tomato_early_blight.jpg"
        
    def test_load_and_validate_image(self):
        if self.sample_img_path.exists():
            img = load_and_validate_image(self.sample_img_path)
            self.assertIsInstance(img, Image.Image)
            self.assertEqual(img.mode, "RGB")
            
    def test_apply_clahe(self):
        if self.sample_img_path.exists():
            img = load_and_validate_image(self.sample_img_path)
            clahe_img = apply_clahe(img)
            self.assertIsInstance(clahe_img, Image.Image)
            self.assertEqual(clahe_img.size, img.size)
            
    def test_preprocess_for_inference(self):
        if self.sample_img_path.exists():
            img = load_and_validate_image(self.sample_img_path)
            batch_tensor, resized = preprocess_for_inference(img, target_size=(224, 224))
            self.assertEqual(batch_tensor.shape, (1, 224, 224, 3))
            self.assertGreaterEqual(float(np.min(batch_tensor)), -1.0)
            self.assertLessEqual(float(np.max(batch_tensor)), 1.0)
            
    def test_foliage_segmentation(self):
        if self.sample_img_path.exists():
            img = load_and_validate_image(self.sample_img_path)
            res = segment_leaf_mask(img)
            self.assertIn("segmented_image", res)
            self.assertIn("lesion_percentage", res)
            self.assertGreaterEqual(res["lesion_percentage"], 0.0)


if __name__ == "__main__":
    unittest.main()

