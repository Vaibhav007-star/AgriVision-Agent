# 🌿 AgriVision Agent: Plant Disease Detection Guide & Code Instructions

Comprehensive documentation explaining the architecture, machine learning libraries, visual processing pipeline, and code instructions used to detect crop diseases in AgriVision Agent.

---

## 1. Libraries and Technologies Used

### A. Python Backend, Training & Server
| Library | Version / Role | Purpose in AgriVision |
| :--- | :--- | :--- |
| **`tensorflow` / `keras`** | Deep Learning Core | Implements **MobileNetV2** Transfer Learning model, layer definitions, Adam optimizer, categorical cross-entropy loss, and model serialization (`.keras` and `.h5`). |
| **`opencv-python` (`cv2`)** | Computer Vision | - **CLAHE** (Contrast Limited Adaptive Histogram Equalization) on LAB color space to enhance lesion textures.<br>- **Color space thresholding** (HSV) for leaf vs. lesion segmentation.<br>- **Laplacian Edge Variance** to reject blank walls or smooth surfaces.<br>- **Grad-CAM colormap rendering** (`cv2.COLORMAP_JET`). |
| **`Pillow` (`PIL`)** | Image I/O & Manipulation | Image loading from multiple formats (JPG, PNG, WebP), dimension verification, Lanczos resampling to 224×224, and RGB conversions. |
| **`numpy`** | Numerical Computing | Matrix operations, tensor reshaping (`[1, 224, 224, 3]`), MobileNet range scaling (`[-1.0, 1.0]`), GLI (Green Leaf Index), and Top-K Softmax sorting. |
| **`fastapi` & `uvicorn`** | Full-Stack REST API | Asynchronous web server hosting the diagnostic scanner, Grad-CAM generation endpoints, and dosage calculation at `http://127.0.0.1:8000`. |
| **`langgraph` & `langchain-groq`** | Agentic AI Advisory | Autonomous agronomic reasoning engine that formulates spray schedules and treatment plans based on detected disease and local weather. |
| **`faiss-cpu` & `sentence-transformers`** | RAG Vector Search | Offline semantic search across agricultural research bulletins and pesticide label databases. |

### B. Flutter Mobile Application (100% Offline Edge AI)
| Package | Role | Purpose in Mobile App |
| :--- | :--- | :--- |
| **`tflite_flutter`** | On-Device Inference Engine | Runs the compiled TensorFlow Lite model (`model.tflite`) directly on mobile CPU/NPU without requiring internet or backend servers. |
| **`image` (Dart)** | Image Processing | Pure Dart image decoding, Lanczos resizing to 224×224, pixel RGB float normalization, and color histogram checks. |
| **`image_picker`** | Camera & Gallery I/O | Captures leaf photos via native camera or imports existing photos from Android gallery. |

---

## 2. How Plant Disease Detection Works (End-to-End Pipeline)

```mermaid
flowchart TD
    A["Raw Photo (Camera / Upload)"] --> B["1. Image Ingestion & Validation"]
    B --> C["2. Botanical & OOD Guardrail"]
    C -->|"Human / Blank / Non-Plant"| D["Reject with Agronomic Advisory"]
    C -->|"Valid Leaf Foliage"| E["3. CLAHE Contrast Enhancement"]
    E --> F["4. Resize to 224x224 & Normalize [-1, 1]"]
    F --> G["5. MobileNetV2 Feature Extractor"]
    G --> H["6. Dense Classification Head + Softmax"]
    H --> I["7. Top-3 Prediction Ranking"]
    I --> J["8. Grad-CAM Heatmap Generation (XAI)"]
    J --> K["9. Agronomic Treatment Formulation"]
```

### Detailed Breakdown of Each Step:

### Step 1: Image Ingestion & Formatting
The input image is decoded, verified for a minimum dimension of $32 \times 32$ pixels, and converted to standardized 3-channel RGB color space.

### Step 2: Botanical & Out-of-Distribution (OOD) Guardrail
Before sending images into the neural network, AgriVision filters out invalid non-plant images:
1. **Texture Check (Laplacian Variance):** Solid walls, blank sheets, or uniform colors have low edge variance ($\sigma^2 < 8.0$) and are rejected.
2. **Skin Color Filter (YCbCr + RGB):** Human skin pixels are identified using chrominance bounds ($130 \le Cr \le 178$ and $75 \le Cb \le 130$). If skin coverage dominates plant foliage, the image is rejected to prevent medical misuse.
3. **Foliage Ratio & GLI:** Plant foliage pixels are identified using Hue bounds ($24 \le H \le 98$) and Green Leaf Index $\text{GLI} = \frac{2G - R - B}{2G + R + B}$. If foliage coverage $< 10\%$, it is rejected.

### Step 3: Computer Vision Enhancement (CLAHE)
The image is converted to **CIE LAB color space**. Contrast Limited Adaptive Histogram Equalization (clip limit 2.0, grid 8×8) is applied specifically to the **L (Luminance) channel**, leaving color channels intact. This amplifies faint fungal pustules, bacterial spot halos, and early chlorotic borders.

### Step 4: Normalization
The image is resized to $224 \times 224 \times 3$ and normalized according to MobileNetV2 specification:
$$\text{Pixel}_{\text{norm}} = \frac{\text{Pixel}}{127.5} - 1.0 \quad \in [-1.0, 1.0]$$

### Step 5 & 6: MobileNetV2 Deep Learning Inference
- **Base Network:** MobileNetV2 with inverted residual bottlenecks and depthwise separable convolutions pre-trained on ImageNet.
- **Classification Head:**
  1. `GlobalAveragePooling2D`
  2. `BatchNormalization`
  3. `Dense(256, activation='relu', kernel_regularizer=L2(1e-4))`
  4. `Dropout(0.35)`
  5. `Dense(128, activation='relu')`
  6. `Dropout(0.20)`
  7. `Dense(15, activation='softmax')`

### Step 7: Explainable AI (Grad-CAM)
AgriVision extracts the gradients of the top predicted class with respect to the final convolutional feature maps (`out_relu` / `Conv2D`). It produces a 2D activation heatmap indicating exactly which leaf lesions and spots triggered the diagnosis, overlaid using OpenCV Jet colormap.

### Step 8: Agronomic Advisory Formulation
The detected disease is mapped to an agronomic database to compute:
- Chemical treatments with exact dosage per liter.
- Organic bio-fungicide alternatives (Neem oil, *Trichoderma*).
- Safe Pre-Harvest Interval (PHI) in days.
- Knapsack spray pump calculations based on user acreage.

---

## 3. Supported Crops and Diseases (15 Trained Classes)

The neural network is trained on 15 classes across **3 crop species**:

| # | Crop | Condition / Disease | Pathogen Type |
| :-: | :--- | :--- | :--- |
| **0** | **Pepper Bell** 🫑 | Bacterial Spot (*Xanthomonas campestris*) | Bacterial |
| **1** | **Pepper Bell** 🫑 | Healthy Leaf | None |
| **2** | **Potato** 🥔 | Early Blight (*Alternaria solani*) | Fungal |
| **3** | **Potato** 🥔 | Healthy Leaf | None |
| **4** | **Potato** 🥔 | Late Blight (*Phytophthora infestans*) | Oomycete |
| **5** | **Tomato** 🍅 | Bacterial Spot (*Xanthomonas*) | Bacterial |
| **6** | **Tomato** 🍅 | Early Blight (*Alternaria solani*) | Fungal |
| **7** | **Tomato** 🍅 | Healthy Leaf | None |
| **8** | **Tomato** 🍅 | Late Blight (*Phytophthora infestans*) | Oomycete |
| **9** | **Tomato** 🍅 | Leaf Mold (*Passalora fulva*) | Fungal |
| **10** | **Tomato** 🍅 | Septoria Leaf Spot (*Septoria lycopersici*) | Fungal |
| **11** | **Tomato** 🍅 | Two-Spotted Spider Mite (*Tetranychus urticae*) | Pest / Acarina |
| **12** | **Tomato** 🍅 | Target Spot (*Corynespora cassiicola*) | Fungal |
| **13** | **Tomato** 🍅 | Tomato Mosaic Virus (ToMV) | Viral |
| **14** | **Tomato** 🍅 | Tomato Yellow Leaf Curl Virus (TYLCV) | Viral |

> [!IMPORTANT]
> **Why Unsupported Crops (like Wheat) are Misdiagnosed:**
> Standard classification models operate under a **"Closed-World Assumption"**. Because the final layer is a Softmax function, the output probabilities across the 15 classes must sum to 100%. 
> If an unsupported crop (such as Wheat with Rust) is submitted, the model has no "Wheat" class and is forced to pick the closest visual match (orange pustules on green tissue match the necrotic spots of Pepper Bacterial Spot).

---

## 4. Code Instructions & Usage Examples

### A. Python Code: Running Single-Image Diagnosis
Save and run this script from the project root:

```python
from pathlib import Path
from PIL import Image
from app.ml.inference import predict_crop_disease

# Path to your test image
image_path = Path("data/samples/sample_tomato_early_blight.jpg")

# Run full inference pipeline
result = predict_crop_disease(
    image_input=image_path,
    compute_gradcam=True
)

if not result["is_leaf"]:
    print(f"[REJECTED] {result['advisory_message']}")
else:
    print(f"Crop:       {result['crop']}")
    print(f"Disease:    {result['disease']}")
    print(f"Confidence: {result['confidence_percentage']}% ({result['confidence_level']})")
    print("\nTop-3 Predictions:")
    for pred in result["top_predictions"]:
        print(f" - #{pred['rank']} {pred['crop']} {pred['disease']}: {pred['confidence_pct']}")
```

### B. Python Code: Running the Web Diagnostic Server
To launch the interactive web dashboard with Grad-CAM viewer:

```powershell
# From project root:
.\run_app.ps1
```
Or directly via Python:
```powershell
.\.venv\Scripts\python.exe app\server.py
```
Then navigate to: `http://127.0.0.1:8000`

### C. Flutter Code: How Mobile App Runs On-Device TFLite
In `mobile/agrivision_app/lib/services/classifier_service.dart`:

```dart
import 'dart:io';
import 'dart:typed_data';
import 'package:flutter/foundation.dart';
import 'package:flutter/services.dart';
import 'package:image/image.dart' as img;
import 'package:tflite_flutter/tflite_flutter.dart';

// 1. Initialize Interpreter
final interpreter = await Interpreter.fromAsset('assets/model.tflite');

// 2. Decode and resize input image
final Uint8List bytes = await imageFile.readAsBytes();
final img.Image? decoded = img.decodeImage(bytes);
final img.Image resized = img.copyResize(decoded!, width: 224, height: 224);

// 3. Prepare normalized float input buffer [-1.0, 1.0]
final Float32List inputBuffer = Float32List(1 * 224 * 224 * 3);
int idx = 0;
for (int y = 0; y < 224; y++) {
  for (int x = 0; x < 224; x++) {
    final pixel = resized.getPixel(x, y);
    inputBuffer[idx++] = (pixel.r / 127.5) - 1.0;
    inputBuffer[idx++] = (pixel.g / 127.5) - 1.0;
    inputBuffer[idx++] = (pixel.b / 127.5) - 1.0;
  }
}

// 4. Run on-device inference
final input = inputBuffer.reshape([1, 224, 224, 3]);
final output = List.filled(15, 0.0).reshape([1, 15]);
interpreter.run(input, output);

// 5. Output probabilities array
List<double> probabilities = List<double>.from(output[0]);
```

### D. Python Code: Retraining or Adding New Crops (e.g., Wheat)
To add Wheat or other species to the model:

```python
import tensorflow as tf
from src.models.model_builder import build_transfer_learning_model

# 1. Update number of classes (e.g. 15 current + 3 wheat rust classes = 18)
model = build_transfer_learning_model(
    num_classes=18,
    input_shape=(224, 224, 3),
    fine_tune_layers=25,
    learning_rate=1e-4
)

# 2. Train on augmented dataset
# model.fit(train_dataset, validation_data=val_dataset, epochs=10)

# 3. Export to TFLite for Mobile Deployment
converter = tf.lite.TFLiteConverter.from_keras_model(model)
converter.optimizations = [tf.lite.Optimize.DEFAULT]  # Dynamic range quantization
tflite_model = converter.convert()

with open("mobile/agrivision_app/assets/model.tflite", "wb") as f:
    f.write(tflite_model)
```
