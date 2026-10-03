# 🌾 AgriVision Agent
### An Agentic AI-Based Crop Disease Detection, Diagnosis & Agricultural Recommendation System

[![Python Version](https://img.shields.io/badge/python-3.11%2B-blue.svg)](https://www.python.org/)
[![Deep Learning](https://img.shields.io/badge/TensorFlow-2.15%2B-orange.svg)](https://www.tensorflow.org/)
[![Agentic AI](https://img.shields.io/badge/LangGraph-State--Based-green.svg)](https://www.langchain.com/)
[![Web Platform](https://img.shields.io/badge/FastAPI-Full--Stack%20Web-009688.svg)](https://fastapi.tiangolo.com/)
[![UI Theme](https://img.shields.io/badge/Theme-Zenze%20Dark%20Agriculture-lime.svg)]()
[![Tests](https://img.shields.io/badge/Tests-83%20Passed-brightgreen.svg)]()

---

## 📌 Project Overview
**AgriVision Agent** is an end-to-end academic deep learning and autonomous agentic AI system designed for real-time agricultural crop disease diagnosis, disease severity estimation, and personalized agronomic advisory.

Built for the **Artificial Neural Networks (ANN) & Deep Learning** curriculum, the system combines:
1. **Computer Vision & CNN Transfer Learning (MobileNetV2)** for fast, highly accurate visual leaf classification.
2. **State-Based AI Agent Workflow (LangGraph)** that reasons over predictions, retrieves authoritative pathology guidance, checks microclimate conditions, and formulates practical biological and chemical treatment plans.
3. **Retrieval-Augmented Generation (RAG)** with FAISS vector indexing for grounded, hallucination-free remedies.
4. **Bilingual Advisory Engine (English & Hindi)** allowing conversational interactions for local farmers.

---

## 🏗️ System Architecture

```text
       ┌───────────────────────────────┐
       │   Farmer / Field Inspector   │
       └──────────────┬────────────────┘
                      │ (Uploads Leaf Photo)
                      ▼
       ┌───────────────────────────────┐
       │  OpenCV Preprocessing & Res   │
       └──────────────┬────────────────┘
                      │ (224x224 RGB Tensor)
                      ▼
       ┌───────────────────────────────┐
       │   Deep Learning Vision CNN    │
       │ (MobileNetV2 Transfer Learn)  │
       └──────────────┬────────────────┘
                      │ (Crop, Disease & Confidence %)
                      ▼
       ┌───────────────────────────────┐
       │  Confidence Gate Validation   │
       └──────────────┬────────────────┘
                      │
           ┌──────────┴──────────┐
           ▼                     ▼
    [High Confidence]     [Low Confidence / Uncertainty]
           │                     │
           │                     └─► Ask Farmer for clearer leaf angle
           ▼
    ┌─────────────────────────────────────────┐
    │     LangGraph Autonomous AI Agent       │
    │                                         │
    │  1. Ingest Prediction & Meta            │
    │  2. Query FAISS Vector Store (RAG)      │
    │  3. Call Weather Tool (Humidity/Rain)   │
    │  4. Synthesize Organic & Chemical Plan  │
    └────────────────────┬────────────────────┘
                         │
                         ▼
    ┌─────────────────────────────────────────┐
    │  Interactive Streamlit UI & Advisory    │
    │  - Top-3 Predictions & Confidence Gauge │
    │  - Formulated Bio-Chemical Prescription │
    │  - English / Hindi Bilingual Chat       │
    │  - Audit Log & SQLite Telemetry         │
    └─────────────────────────────────────────┘
```

---

## 🚀 Key Features

- **Leaf Disease Classification:** Multi-class classification across major staples (Tomato, Potato, Corn, Apple, Grape, Pepper).
- **Transfer Learning Backbone:** Lightweight MobileNetV2 architecture fine-tuned for high accuracy on standard student hardware.
- **RAG-Powered Agronomic Prescriptions:** Vector search through pathology databases for verified chemical dosages and organic solutions.
- **Microclimate-Aware Reasoning:** Incorporates ambient temperature, relative humidity, and spore germination risk indices.
- **Bilingual Conversational Interface:** Real-time conversational farmer assistant in English and Hindi (हिंदी).
- **Full Audit Logging:** SQLite database automatically records all scans, predictions, and recommendations.

---

## 🛠️ Tech Stack

| Domain | Technology |
| :--- | :--- |
| **Language** | Python 3.11+ |
| **Deep Learning** | TensorFlow 2.15+, Keras, MobileNetV2 / EfficientNetB0 |
| **Computer Vision** | OpenCV, Pillow |
| **Agentic Framework** | LangGraph, LangChain Core & Community |
| **LLM Connectors** | Groq (Llama 3.3), Google Gemini, Local Ollama |
| **Vector DB / RAG** | FAISS (CPU), Sentence-Transformers |
| **Frontend UI** | Streamlit |
| **Storage** | SQLite3 / SQLAlchemy |

---

## 📂 Project Directory Structure

```text
AgriVision-Agent/
├── app/
│   ├── main.py               # Streamlit application entry point & router
│   ├── config.py             # Application & service configuration
│   ├── ui/                   # Modular UI page views
│   │   ├── home.py           # Overview & system architecture
│   │   ├── detection.py      # Leaf upload, CV preprocessing & Grad-CAM
│   │   ├── agent.py          # LangGraph state machine & knapsack dosage
│   │   ├── dashboard.py      # Health ratios & disease telemetry
│   │   ├── history.py        # SQLite diagnostic audit logs
│   │   └── chatbot.py        # Bilingual farmer conversational advisory
│   ├── agent/                # LangGraph state machine, nodes & tools
│   │   ├── graph.py
│   │   ├── state.py
│   │   ├── nodes/
│   │   ├── tools/
│   │   └── prompts/
│   ├── ml/                   # Machine learning architectures & inference
│   │   ├── model.py          # Custom CNN & MobileNetV2 (with ANN layer breakdown)
│   │   ├── preprocessing.py  # CLAHE & normalizer
│   │   ├── inference.py      # Confidence gating & Grad-CAM
│   │   └── evaluation.py     # Metrics engine
│   ├── rag/                  # Retrieval-Augmented Generation
│   │   ├── vectorstore.py    # FAISS dense vector search
│   │   └── knowledge_base.py # Grounded prescriptions
│   ├── database/             # SQLite storage engine
│   │   ├── database.py       # Connection manager
│   │   ├── models.py         # Schemas & dataclasses
│   │   └── crud.py           # Database operations
│   └── services/             # Environmental & localization services
│       ├── weather.py        # Microclimate spore risk evaluator
│       └── translation.py    # English <-> Hindi glossary
├── data/
│   ├── raw/                  # Raw dataset storage (e.g. Tomato Early/Late/Healthy)
│   ├── processed/            # Preprocessed train/val/test splits & FAISS index
│   └── README.md             # Dataset download & preprocessing guide
├── models/
│   ├── mobilenet_model.keras # Serialized trained MobileNetV2 model
│   └── class_names.json      # Target class label mappings
├── knowledge/
│   ├── documents/            # Agricultural pathology manuals
│   └── vectorstore/          # FAISS vector store indices
├── notebooks/                # Academic experimentation Jupyter notebooks
├── tests/                    # Unit and integration tests (76 tests)
├── reports/                  # Confusion matrix, classification report & loss curves
├── scripts/                  # Standalone CLI tools (train.py, evaluate.py, ingest_knowledge.py)
├── uploads/                  # User leaf uploads
├── config.yaml               # Master ML & Dataset configuration
├── .env.example              # Environment variables template
├── .gitignore                # Git exclusions
├── requirements.txt          # Python project dependencies
├── README.md                 # Project documentation
├── PROJECT_STATUS.md         # Phase-by-phase execution status
└── LICENSE                   # MIT Academic License
```

---

## 💻 Quick Start & Running

### 1. Clone & Set Up Environment
```powershell
# Create Python 3.11 virtual environment
py -3.11 -m venv .venv

# Activate virtual environment
.venv\Scripts\Activate.ps1
```

### 2. Install Dependencies
```powershell
pip install -r requirements.txt
```

### 3. Configure Environment Variables
```powershell
copy .env.example .env
```
*(Optional for Phase 1; keys can be added for Groq/Gemini in Phase 5).*

### 4. Launch Application
```powershell
# Launch the Zenze-Themed Full-Stack Web Platform (FastAPI + PWA)
python app/server.py

# Or double-click the Windows batch script
.\run_app.bat
```
Open your browser at **`http://localhost:8000`**.

---

## 📱 Mobile App (100% Offline Flutter + TFLite)

AgriVision also includes a fully offline cross-platform mobile application located in `mobile/agrivision_app/`:

- **Zero-Internet Inference:** Uses TensorFlow Lite (`tflite_flutter`) to classify crop diseases in <50ms entirely on-device without internet or server access.
- **On-Device Agricultural Database:** Bundles a comprehensive 15-class disease encyclopedia with treatment plans, organic remedies, and prevention tips.
- **Offline Knapsack Spray & Fertilizer Dosage Calculator:** Calculates water and chemical quantities based on field acreage, spray equipment, and recommended spray volume.
- **Bilingual Interface:** Supports English and Hindi for rural accessibility.
- **Production Build:**
  ```powershell
  cd mobile/agrivision_app
  flutter build apk --release --target-platform android-arm64
  ```
  The generated APK is stored at `mobile/agrivision_app/build/app/outputs/flutter-apk/app-release.apk`.

