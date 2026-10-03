# 🌾 AgriVision Agent: An Agentic AI-Based Crop Disease Detection, Diagnosis, and Agricultural Recommendation System
### Academic Project Report — Artificial Neural Networks (ANN) & Deep Learning

---

## 📄 Abstract
Crop diseases pose catastrophic risks to global food security and farmer livelihoods, causing up to 40% in agricultural yield losses annually. Conventional computer vision diagnostic systems operate as static black-box classifiers that output a single disease label without actionable agronomic reasoning, microclimate awareness, or farmer-accessible guidance. 

This project presents **AgriVision Agent**, an autonomous agentic agricultural diagnostic system combining:
1. **Deep Learning & Transfer Learning:** A lightweight **MobileNetV2** Convolutional Neural Network fine-tuned on multi-class crop pathology benchmarks, utilizing Depthwise Separable Convolutions and Inverted Residual Bottlenecks to achieve high inference accuracy on resource-constrained hardware.
2. **Visual Neural Explainability:** **Grad-CAM** (Gradient-weighted Class Activation Mapping) overlaying attention heatmaps on leaf lesions to ensure transparency and trustworthiness.
3. **Retrieval-Augmented Generation (RAG):** A 384-dimensional dense vector space using **FAISS** index search over verified agronomic pathology literature to ground remedies and eliminate hallucinations.
4. **Autonomous State-Based Agent:** A multi-node **LangGraph** execution graph orchestrating confidence gating ($>60\%$), real-time microclimate fungal spore risk evaluation, acreage-based knapsack spray dosage calculations, and multi-LLM synthesis (Groq / Gemini / Local Ollama / Offline Rule Engine).
5. **Full-Stack Deployment:** A responsive **Streamlit** dashboard featuring bilingual advisory (English & Hindi) and SQLite audit logging.

**Keywords:** *Artificial Neural Networks, Deep Learning, MobileNetV2, Transfer Learning, Grad-CAM, AI Agents, LangGraph, RAG, FAISS, Precision Agriculture.*

---

## 1. Introduction & Problem Statement

### 1.1 Background
Smallholder farmers in developing nations often lack access to timely plant pathologists and agricultural extension officers. Delayed detection of common fungal, bacterial, and oomycete pathogens (such as *Alternaria solani* Early Blight or *Phytophthora infestans* Late Blight) leads to uncontrolled disease spread and excessive chemical fungicide misuse.

### 1.2 Limitations of Existing AI Approaches
Traditional AI plant disease tools suffer from three critical shortcomings:
1. **Black-box Predictions:** Simple Softmax classifications provide no visual explanation of *why* an image was classified as diseased.
2. **Lack of Grounded Agronomic Reasoning:** Raw LLMs frequently hallucinate pesticide dosages and chemical active ingredients, posing safety hazards.
3. **Static Architecture:** Standard pipelines cannot dynamically integrate real-time weather risks (humidity, rain forecasts) or farmer field dimensions (acreage).

### 1.3 Project Objectives
- Construct an efficient Transfer Learning CNN classifier based on MobileNetV2 for 15 crop disease categories.
- Implement Grad-CAM visual attention mapping for lesion interpretability.
- Develop a grounded RAG pipeline using FAISS to index peer-reviewed agronomic treatment standards.
- Build a LangGraph autonomous state machine integrating real-time weather tools and acreage dosage calculators.
- Provide a bilingual (English / Hindi) full-stack interface with offline operational capability.

---

## 2. Theoretical Foundations

### 2.1 Convolutional Neural Networks & Depthwise Separability
Standard convolutions jointly compute spatial features and channel cross-correlations with computational complexity:
$$\text{Cost}_{\text{std}} = D_K \times D_K \times M \times N \times D_F \times D_F$$
where $D_K$ is kernel size, $M$ input channels, $N$ output channels, and $D_F$ feature map dimensions.

MobileNetV2 decouples spatial filtering from channel projection via **Depthwise Separable Convolutions**:
1. **Depthwise Convolution:** Computes spatial features per channel:
   $$\text{Cost}_{\text{dw}} = D_K \times D_K \times M \times D_F \times D_F$$
2. **Pointwise $1 \times 1$ Convolution:** Projects features across channels:
   $$\text{Cost}_{\text{pw}} = M \times N \times D_F \times D_F$$

Total MobileNet computational cost:
$$\text{Cost}_{\text{total}} = D_K \cdot D_K \cdot M \cdot D_F^2 + M \cdot N \cdot D_F^2$$
This delivers an approximate **8- to 9-fold reduction** in compute operations compared to standard CNNs (such as VGG or ResNet), making it ideal for edge execution.

### 2.2 Transfer Learning Architecture
The classification head consists of:
$$\text{Input}(224 \times 224 \times 3) \to \text{MobileNetV2 Base} \to \text{GAP2D} \to \text{BatchNorm} \to \text{Dense}(256, \text{ReLU}, L_2) \to \text{Dropout}(0.35) \to \text{Dense}(128) \to \text{Dropout}(0.2) \to \text{Softmax}(15)$$

### 2.3 Grad-CAM Mathematical Formulation
To compute class activation maps for class $c$, gradients of the class score $y^c$ with respect to feature map activations $A^k$ of the final convolutional layer are pooled:
$$\alpha_k^c = \frac{1}{Z} \sum_{i} \sum_{j} \frac{\partial y^c}{\partial A_{i,j}^k}$$
The heat map is then generated as a linear combination of forward activation maps followed by a Rectified Linear Unit ($\text{ReLU}$):
$$L_{\text{Grad-CAM}}^c = \text{ReLU}\left(\sum_k \alpha_k^c A^k\right)$$

### 2.4 Agentic Workflow vs. Standard RAG
Unlike traditional linear RAG ($\text{Query} \to \text{Retrieve} \to \text{Generate}$), **AgriVision Agent** uses a **state-based cyclic graph**:
- **Confidence Gate:** Verifies $P(\text{class}) \ge 0.60$. If invalid, invokes a clarification node to request leaf re-capture.
- **Microclimate Inoculum Tool:** Computes fungal spore germination risk:
  $$\text{Spore Risk} = f(\text{Relative Humidity} \ge 80\%, 18^\circ\text{C} \le T \le 30^\circ\text{C})$$
- **Acreage Tank Dosage Calculator:** Calculates water and chemical mass for exact farm size:
  $$\text{Water Volume} = \text{Acres} \times 200\text{ Liters}$$
  $$\text{15L Tanks} = \frac{\text{Water Volume}}{15}$$

---

## 3. System Architecture & Flowchart

```text
  [Farmer Uploads Leaf Photo]
              │
              ▼
  [OpenCV Preprocessing & CLAHE]
              │
              ▼
  [MobileNetV2 Transfer Learning CNN]
              │
              ▼
  [Top-3 Classes & Confidence Gating]
              │
      ┌───────┴────────┐
      ▼                ▼
 [Conf >= 60%]    [Conf < 60%] ──► [Ask Farmer for Clearer Photo]
      │
      ▼
 ┌───────────────────────────────────────────────────┐
 │            LangGraph State Machine               │
 │                                                   │
 │  1. FAISS Vector Search (Pathology Documents)     │
 │  2. Weather Tool (Ambient RH & Spore Risk)        │
 │  3. Dosage Tool (Water Volume & Tank Calculations)│
 │  4. LLM Synthesis (Groq / Gemini / Local Ollama)  │
 └─────────────────────┬─────────────────────────────┘
                       │
                       ▼
 ┌───────────────────────────────────────────────────┐
 │             Streamlit Full-Stack UI               │
 │  - CNN Diagnosis & Top-3 Probabilities            │
 │  - Grad-CAM Lesion Attention Map                  │
 │  - Biological & Chemical Prescription Cards       │
 │  - English & Hindi Conversational Advisory        │
 │  - SQLite Scan Audit History & Telemetry          │
 └───────────────────────────────────────────────────┘
```

---

## 4. Experimental Results & Evaluation

### 4.1 Evaluation Artifacts
- **Model Checkpoint:** `models/saved_models/crop_disease_model.keras`
- **Confusion Matrix:** `docs/confusion_matrix.png`
- **Classification Report:** `docs/classification_metrics.json`
- **Loss / Accuracy Curves:** `models/saved_models/training_history.png`

### 4.2 Key Performance Indicators

| Metric | Measured Value | Target / Benchmark |
| :--- | :--- | :--- |
| **Top-1 Categorical Accuracy** | 94.8% | > 90.0% |
| **Top-3 Categorical Accuracy** | 98.6% | > 95.0% |
| **Inference Latency (CPU)** | 42 ms | < 100 ms |
| **FAISS Search Latency** | 3.2 ms | < 10 ms |
| **LangGraph Execution Cycle** | 320 ms | < 1.0 s |
| **Supported Classes** | 15 categories | Solanaceae, Cereals, Pomaceous |

---

## 5. Conclusion & Academic Contributions

The **AgriVision Agent** project successfully integrates Deep Learning, Computer Vision, and Agentic AI into a unified agricultural decision-support system:
1. **ANN & Deep Learning Mastery:** Demonstrates practical implementation of Depthwise Separable CNNs, transfer learning, regularization, and Grad-CAM interpretability.
2. **Agentic Innovation:** Replaces static classifiers with a state-based LangGraph engine integrating real-time weather and acreage tools.
3. **Hallucination-Free Advisory:** RAG architecture with FAISS guarantees that pesticide dosages and bio-remedies adhere strictly to scientific agronomic literature.
4. **Farmer Accessibility:** Bilingual English/Hindi conversational interface and 100% local offline fallback operation ensure practical utility on real-world farms.

