"""
Unit tests for Computer Vision, Image Preprocessing, and Dataset tools.
"""

import unittest
from pathlib import Path
from PIL import Image
import numpy as np

from src.utils.image_processing import (
    load_and_validate_image,
    preprocess_for_model,
    apply_clahe_enhancement,
    segment_leaf_mask,
    extract_leaf_features
)
from src.utils.dataset import generate_benchmark_sample_images, get_available_samples, load_class_indices


class TestImageProcessing(unittest.TestCase):
    
    def setUp(self):
        # Create a temporary synthetic RGB test image
        self.test_img = Image.new("RGB", (250, 250), color=(50, 160, 60))
        
    def test_load_and_validate_image(self):
        validated = load_and_validate_image(self.test_img)
        self.assertEqual(validated.mode, "RGB")
        self.assertEqual(validated.size, (250, 250))
        
    def test_preprocess_for_model(self):
        tensor = preprocess_for_model(self.test_img, target_size=(224, 224), normalization="mobilenet")
        self.assertEqual(tensor.shape, (1, 224, 224, 3))
        self.assertGreaterEqual(np.min(tensor), -1.0)
        self.assertLessEqual(np.max(tensor), 1.0)
        
    def test_clahe_enhancement(self):
        enhanced = apply_clahe_enhancement(self.test_img)
        self.assertEqual(enhanced.size, self.test_img.size)
        self.assertEqual(enhanced.mode, "RGB")
        
    def test_segment_leaf_mask(self):
        result = segment_leaf_mask(self.test_img)
        self.assertIn("mask_image", result)
        self.assertIn("segmented_image", result)
        self.assertIn("lesion_percentage", result)
        self.assertIsInstance(result["lesion_percentage"], float)
        
    def test_extract_leaf_features(self):
        features = extract_leaf_features(self.test_img)
        self.assertIn("mean_green_leaf_index", features)
        self.assertIn("mean_vari_index", features)
        
    def test_sample_generation(self):
        paths = generate_benchmark_sample_images()
        self.assertGreater(len(paths), 0)
        sample_dict = get_available_samples()
        self.assertGreater(len(sample_dict), 0)
        
    def test_class_indices_load(self):
        indices = load_class_indices()
        self.assertIn(0, indices)
        self.assertIn("crop", indices[0])
        self.assertIn("disease", indices[0])


if __name__ == "__main__":
    unittest.main()

