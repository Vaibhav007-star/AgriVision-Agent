"""
Unit and Integration tests for Dataset Preparation & Preprocessing Pipeline (Phase 2).
"""

import unittest
from pathlib import Path
import json
from PIL import Image

from ml.data.prepare_dataset import load_yaml_config, validate_dataset
from ml.preprocessing.preprocess import process_image, apply_realistic_augmentation, run_preprocessing_pipeline


class TestDatasetPreprocessing(unittest.TestCase):
    
    def setUp(self):
        self.base_dir = Path(__file__).resolve().parent.parent
        self.config_path = self.base_dir / "config.yaml"
        self.raw_dir = self.base_dir / "data" / "raw"
        self.processed_dir = self.base_dir / "data" / "processed"
        
    def test_config_loading(self):
        cfg = load_yaml_config(self.config_path)
        self.assertIn("dataset", cfg)
        self.assertIn("model", cfg)
        self.assertEqual(cfg["dataset"]["image_size"], [224, 224])
        self.assertIn("selected_classes", cfg["dataset"])
        
    def test_dataset_validation(self):
        cfg = load_yaml_config(self.config_path)
        classes = cfg["dataset"]["selected_classes"]
        report = validate_dataset(self.raw_dir, classes)
        self.assertTrue(report["valid"])
        self.assertGreaterEqual(report["total_images"], len(classes) * 10)
        
    def test_image_processing_dimensions(self):
        # Pick any image in raw_dir
        sample_img_path = next(self.raw_dir.glob("*/*.jpg"))
        processed_img = process_image(sample_img_path, (224, 224))
        self.assertEqual(processed_img.size, (224, 224))
        self.assertEqual(processed_img.mode, "RGB")
        
    def test_realistic_augmentation(self):
        sample_img_path = next(self.raw_dir.glob("*/*.jpg"))
        processed_img = process_image(sample_img_path, (224, 224))
        aug_cfg = {
            "rotation_range_degrees": 20,
            "horizontal_flip": True,
            "zoom_range": [0.85, 1.15],
            "brightness_range": [0.85, 1.15]
        }
        augmented = apply_realistic_augmentation(processed_img, aug_cfg)
        self.assertEqual(augmented.size, (224, 224))
        self.assertEqual(augmented.mode, "RGB")
        
    def test_preprocessing_pipeline_artifacts(self):
        summary_file = self.processed_dir / "dataset_summary.json"
        indices_file = self.processed_dir / "class_indices.json"
        self.assertTrue(summary_file.exists())
        self.assertTrue(indices_file.exists())
        
        with open(summary_file, "r", encoding="utf-8") as f:
            summary = json.load(f)
            self.assertGreater(summary["splits"]["train"], 0)
            self.assertGreater(summary["splits"]["val"], 0)
            self.assertGreater(summary["splits"]["test"], 0)


if __name__ == "__main__":
    unittest.main()

