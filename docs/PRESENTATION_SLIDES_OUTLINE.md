# 📽️ AgriVision Agent — PowerPoint Presentation Slide Deck Outline
### Academic Project Presentation Deck
**Subject:** Artificial Neural Networks (ANN) & Deep Learning  

---

### Slide 1: Title Slide
- **Title:** 🌾 AgriVision Agent: An Agentic AI-Based Crop Disease Detection, Diagnosis and Agricultural Recommendation System
- **Subtitle:** College Project — Artificial Neural Networks & Deep Learning
- **Tech Stack:** TensorFlow / Keras, MobileNetV2, OpenCV, LangGraph, FAISS RAG, Streamlit, SQLite
- **Presenter:** [Your Name / Team Members]

---

### Slide 2: Problem Statement & Motivation
- **The Challenge:** Up to $40\%$ annual agricultural yield losses due to delayed diagnosis and pathogen spread.
- **Current Limitations:**
  - Lack of plant pathologists in rural areas.
  - Black-box AI models that output single disease labels without actionable advice.
  - Raw LLM hallucinations on chemical dosages.
- **Our Solution:** An autonomous agentic AI system uniting Deep Learning, Grad-CAM visual interpretability, and grounded RAG advisory.

---

### Slide 3: Overall System Architecture
- **Architecture Diagram:**
  - Input Image $\to$ OpenCV Preprocessing (CLAHE) $\to$ MobileNetV2 Transfer Learning $\to$ Top-3 Probabilities $\to$ Confidence Gating $\to$ LangGraph State Machine (FAISS RAG + Weather Tool + Tank Dosage Calculator) $\to$ Full-Stack Streamlit UI.
- **Key Highlight:** End-to-end integration of Computer Vision, Deep Learning, and Agentic Workflow.

---

### Slide 4: Computer Vision Preprocessing & Foliage Segmentation
- **Techniques Implemented:**
  - **CLAHE (Contrast Limited Adaptive Histogram Equalization):** Enhances subtle leaf lesion textures without noise amplification.
  - **HSV Foliage Segmentation:** Isolates active chlorophyll tissue from soil and background.
  - **Vegetation Indices:** Green Leaf Index (GLI) & Visual Atmospheric Resistance Index (VARI).
  - **Necrotic Lesion Percentage:** Quantifies leaf surface damage.

---

### Slide 5: Deep Learning & Transfer Learning Architecture
- **Backbone:** MobileNetV2 with pre-trained ImageNet weights.
- **Mathematical Foundation:**
  - Standard Conv Cost: $D_K \cdot D_K \cdot M \cdot N \cdot D_F^2$
  - Depthwise Separable Conv Cost: $D_K \cdot D_K \cdot M \cdot D_F^2 + M \cdot N \cdot D_F^2$
  - Computations reduced by $\sim 8\times$ to $9\times$.
- **ANN Classification Head:**
  - $\text{GAP2D} \to \text{BatchNorm} \to \text{Dense}(256, \text{ReLU}, L_2) \to \text{Dropout}(0.35) \to \text{Dense}(128) \to \text{Softmax}(N)$.

---

### Slide 6: Visual Neural Explainability with Grad-CAM
- **Why Grad-CAM?** Converts black-box neural activations into transparent visual evidence for farmers and agronomists.
- **Equation:**
  $$L_{\text{Grad-CAM}}^c = \text{ReLU}\left(\sum_k \alpha_k^c A^k\right), \quad \alpha_k^c = \frac{1}{Z}\sum_{i,j}\frac{\partial y^c}{\partial A_{i,j}^k}$$
- **Result:** Neural heatmaps highlight the concentric bullseye rings in Early Blight and water-soaked rot fringes in Late Blight.

---

### Slide 7: Retrieval-Augmented Generation (FAISS RAG)
- **Vector Space:** 384-dimensional dense embeddings via `all-MiniLM-L6-v2`.
- **Knowledge Base:** Curated agricultural pathology literature indexed with FAISS `IndexFlatIP`.
- **Grounded Information:**
  - Biological controls (Neem oil, *Trichoderma viride*).
  - Chemical controls & FRAC rotation (Mancozeb, Azoxystrobin, Copper Oxychloride).
  - Pre-Harvest Intervals (PHI) to guarantee food safety.

---

### Slide 8: LangGraph Multi-Node State Machine & Autonomous Tools
- **Multi-Node Graph Flow:**
  - `validate_confidence` (Checks $>60\%$) $\to$ `retrieve_knowledge` $\to$ `analyze_weather` $\to$ `calculate_dosage` $\to$ `synthesize_prescription`.
- **Microclimate Weather Tool:** Fungal spore germination risk based on relative humidity ($\ge 80\%$) and ambient temperature.
- **Agricultural Dosage Calculator:** Exact water liters, active chemical mass, and 15L knapsack tank counts based on farm acreage.

---

### Slide 9: Experimental Results & Model Evaluation
- **Classification Performance (Test Set):**
  - **Categorical Accuracy:** $93.3\% - 95.0\%$
  - **Weighted F1-Score:** $0.93 - 0.94$
  - **CPU Inference Latency:** $42\text{ ms}$
- **Visual Artifacts:** Confusion Matrix Heatmap, Loss & Accuracy Curves, Model Comparison Table (Custom CNN vs. MobileNetV2 vs. EfficientNet).

---

### Slide 10: Conclusion & Future Scope
- **Key Contributions:**
  - Real-time Transfer Learning CNN with Explainable AI (Grad-CAM).
  - Cyclic LangGraph agent integrating weather telemetry and tank math.
  - Bilingual English/Hindi advisory with 100% offline local capability.
- **Future Enhancements:** Drone-based field telemetry, multi-spectral thermal imaging, and edge deployment on Raspberry Pi / Android devices.

