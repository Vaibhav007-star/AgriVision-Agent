# 🌾 AgriVision Agent — Dataset Guide & Documentation

This directory contains the dataset pipeline for **AgriVision Agent**, designed to work with both **development sample mini-datasets** and the **full PlantVillage benchmark dataset**.

---

## 1. Dataset Overview

- **Primary Dataset:** [PlantVillage Dataset](https://www.kaggle.com/datasets/emmarex/plantdisease) (Open Access)
- **Authors:** David Hughes and Marcel Salathé (Penn State University & EPFL)
- **Domain:** Agricultural plant leaf images categorized across healthy and diseased conditions.
- **Full Dataset Size:** ~54,306 images across 38 distinct crop-disease classes (~1.8 GB compressed, ~3.2 GB uncompressed).

---

## 2. Development vs. Full Dataset Modes

To accommodate student hardware and rapid local iteration, AgriVision supports two modes configured in `config.yaml`:

| Mode | Active Classes | Images per Class | Total Images | Recommended Usage |
| :--- | :--- | :--- | :--- | :--- |
| **Development Sample Mode** *(Current)* | 3 Classes (`Tomato___Early_blight`, `Tomato___Late_blight`, `Tomato___healthy`) | ~30 images | ~90 images | Fast pipeline verification, local CPU training, end-to-end testing |
| **Full Production Mode** | 38 Classes (Apple, Corn, Grape, Potato, Tomato, Pepper, etc.) | ~1,000 - 2,000 | ~54,306 | Final GPU training & comprehensive deployment |

---

## 3. Directory Structure

The `data/` directory is structured as follows:

```text
data/
├── raw/                              # Source images organized by class folder
│   ├── Tomato___Early_blight/        # Raw leaf images for Early Blight
│   │   ├── image_001.jpg
│   │   └── ...
│   ├── Tomato___Late_blight/         # Raw leaf images for Late Blight
│   │   ├── image_001.jpg
│   │   └── ...
│   └── Tomato___healthy/             # Raw leaf images for Healthy Tomato
│       ├── image_001.jpg
│       └── ...
│
├── processed/                        # Preprocessed & stratified dataset splits
│   ├── train/                        # 70% Training Split (with Augmentations)
│   │   ├── Tomato___Early_blight/
│   │   ├── Tomato___Late_blight/
│   │   └── Tomato___healthy/
│   ├── val/                          # 15% Validation Split
│   │   ├── Tomato___Early_blight/
│   │   ├── Tomato___Late_blight/
│   │   └── Tomato___healthy/
│   ├── test/                         # 15% Test Split (Held-out evaluation)
│   │   ├── Tomato___Early_blight/
│   │   ├── Tomato___Late_blight/
│   │   └── Tomato___healthy/
│   ├── dataset_summary.json          # Split statistics and distribution
│   └── class_indices.json            # Class label mapping
│
├── sample_images/                    # Test benchmark images for live Streamlit UI demo
├── rag_docs/                         # Markdown agricultural pathology knowledge base
└── README.md                         # This documentation file
```

---

## 4. How to Download the Full PlantVillage Dataset (Optional)

If you wish to train on the complete 54,000+ image dataset:

### Required Resources:
- **Disk Space:** ~3.5 GB free storage.
- **Recommended Hardware:** Dedicated GPU (CUDA) or Google Colab / Kaggle Notebook.

### Download Steps:
1. **Via Kaggle CLI:**
   ```bash
   kaggle datasets download -d emmarex/plantdisease
   ```
2. **Via Browser:**
   - Download the ZIP from [Kaggle Plant Disease Dataset](https://www.kaggle.com/datasets/emmarex/plantdisease) or [PlantVillage GitHub](https://github.com/spMohanty/PlantVillage-Dataset).
3. **Extraction:**
   - Extract the class subfolders directly into `data/raw/`.
4. **Configuration:**
   - In `config.yaml`, set `use_full_dataset: true`.
   - Run the preprocessing pipeline:
     ```bash
     python ml/preprocessing/preprocess.py
     ```

---

## 5. Preprocessing & Data Augmentation Pipeline

The preprocessing script (`ml/preprocessing/preprocess.py`) performs:
1. **Image Validation:** Verifies image dimensions (minimum $32 \times 32$), formats (JPEG/PNG), and forces 3-channel RGB.
2. **Resizing:** High-quality Lanczos interpolation to $224 \times 224 \times 3$ (standard for MobileNetV2 / EfficientNet).
3. **Normalization:** Scales pixel intensities from $[0, 255]$ to $[-1.0, 1.0]$ using MobileNetV2 preprocessing:
   $$x_{\text{norm}} = \frac{x}{127.5} - 1.0$$
4. **Stratified Splitting:** $70\%$ Train, $15\%$ Validation, $15\%$ Test splits with fixed random seed (42) for reproducibility.
5. **Realistic Augmentation:** Applied exclusively to the training set to prevent overfitting:
   - Random rotation ($\pm 20^\circ$)
   - Horizontal flip (true)
   - Vertical flip (disabled to maintain realistic field orientation)
   - Zoom range ($0.85\times$ to $1.15\times$)
   - Translation / Shift ($\pm 10\%$)
   - Brightness variation ($\pm 15\%$) to mimic outdoor sunlight conditions.

