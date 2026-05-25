# 🛡️ FraudShield — Real-Time AI Fraud Detection System

![Python](https://img.shields.io/badge/Python-3.10-blue?style=flat-square&logo=python)
![PyTorch](https://img.shields.io/badge/PyTorch-2.6-red?style=flat-square&logo=pytorch)
![FastAPI](https://img.shields.io/badge/FastAPI-0.136-green?style=flat-square&logo=fastapi)
![Streamlit](https://img.shields.io/badge/Streamlit-Live-ff4b4b?style=flat-square&logo=streamlit)
![Snowflake](https://img.shields.io/badge/Snowflake-Cloud%20DB-29B5E8?style=flat-square&logo=snowflake)
![Railway](https://img.shields.io/badge/Railway-Deployed-0B0D0E?style=flat-square&logo=railway)

> A production-grade fraud detection system powered by Graph Neural Networks, trained on 590,000 real financial transactions from the IEEE-CIS dataset. Deployed with a live API and interactive dashboard.

## 🌐 Live Demo

| Component | URL |
|-----------|-----|
| 🎨 Dashboard | [fraudshield-varun.streamlit.app](https://fraudshield-varun.streamlit.app) |
| ⚡ API Docs | [fraud-detection-gnn-production.up.railway.app/docs](https://fraud-detection-gnn-production.up.railway.app/docs) |

---

## 🏗️ System Architecture

```
User Input → Streamlit Dashboard
                    ↓
            FastAPI REST API (Railway Cloud)
                    ↓
    ┌──────────────────────────────┐
    │   GraphSAGE GNN              │
    │   13,553 nodes, 590K edges   │
    │   (Graph Feature Extraction) │
    └──────────────┬───────────────┘
                   ↓
    ┌──────────────────────────────┐
    │   Random Forest Classifier   │
    │   31 features, 100K samples  │
    │   (Fraud Classification)     │
    └──────────────┬───────────────┘
                   ↓
         Prediction Result
                   ↓
    Snowflake Cloud Data Warehouse
    (Every prediction logged)
```

---

## 🧠 ML Pipeline

### Stage 1 — Data Pipeline
- Loaded and merged **590,540 transactions** from IEEE-CIS dataset
- Handled **434 features**, dropped columns with >50% missing values
- Label encoded categorical features, filled missing values with median
- Saved preprocessed data as optimized pickle format

### Stage 2 — Graph Neural Network (GraphSAGE)
- Built a **heterogeneous transaction graph** — nodes = unique cards (13,553), edges = transactions (590,540)
- Implemented **GraphSAGE** with 2 convolution layers using PyTorch Geometric
- Added **LSTM temporal encoder** for time-aware fraud pattern detection
- Used **permutation-based feature importance** to identify top fraud signals (C2 and C4)
- Trained with **class-weighted loss** to handle 3.5% fraud imbalance

### Stage 3 — Random Forest Classifier
- Trained on **100K real transactions** with **31 behavioral features**
- Handled class imbalance using `class_weight='balanced'`
- Achieved **84% accuracy** and **67% fraud recall**
- Saved model, scaler and feature columns as pickle files

### Stage 4 — Real-time Inference
- **FastAPI** REST endpoint serves predictions in milliseconds
- Every prediction **automatically logged** to **Snowflake** cloud data warehouse
- Full risk factor breakdown with explainability output

---

## 📊 Model Performance

| Metric | Score |
|--------|-------|
| Overall Accuracy | 84% |
| Fraud Recall | 67% |
| Legitimate Precision | 99% |
| Training Samples | 100,000 |
| Features | 31 behavioral |
| Graph Nodes | 13,553 |
| Graph Edges | 590,540 |
| Dataset Size | 590,540 transactions |

---

## 🛠️ Tech Stack

| Layer | Technology |
|-------|-----------|
| **Graph ML** | PyTorch Geometric, GraphSAGE, LSTM |
| **ML Model** | Scikit-learn Random Forest |
| **Explainability** | Permutation Feature Importance |
| **API** | FastAPI + Uvicorn |
| **Dashboard** | Streamlit + Plotly |
| **Database** | Snowflake Cloud Data Warehouse |
| **API Deployment** | Railway |
| **Dashboard Deployment** | Streamlit Community Cloud |
| **Dataset** | IEEE-CIS Fraud Detection (Kaggle) |

---

## 📁 Project Structure

```
fraud-detection-gnn/
├── src/
│   └── app.py                        # FastAPI REST API
├── dashboard/
│   └── dashboard.py                  # Streamlit dashboard
├── notebooks/
│   ├── 01_data_exploration.ipynb     # EDA on 590K transactions
│   ├── 02_preprocessing.ipynb        # Feature engineering
│   ├── 03_graph_building.ipynb       # PyG graph construction
│   └── 04_gnn_model.ipynb            # GNN training + evaluation
├── models/
│   ├── fraud_classifier.pkl          # Trained Random Forest
│   ├── scaler.pkl                    # StandardScaler
│   └── feature_cols.pkl              # Feature column names
├── Procfile                          # Railway deployment config
├── requirements.txt                  # Streamlit dependencies
├── requirements-api.txt              # API dependencies
└── README.md
```

---

## 🚀 Run Locally

```bash
# Clone the repo
git clone https://github.com/varunsajinair/fraud-detection-gnn.git
cd fraud-detection-gnn

# Create conda environment
conda create -n fraudgnn python=3.10
conda activate fraudgnn

# Install API dependencies
pip install -r requirements-api.txt

# Start FastAPI
uvicorn src.app:app --reload

# Open new terminal and start dashboard
pip install -r requirements.txt
streamlit run dashboard/dashboard.py
```

---

## 🔌 API Usage

**Endpoint:** `POST /predict`

```python
import requests

response = requests.post(
    "https://fraud-detection-gnn-production.up.railway.app/predict",
    json={
        "TransactionAmt": 150.0,
        "C1": 1.0,
        "C2": 1.0,
        "C4": 0.0,
        "C5": 0.0
    }
)

print(response.json())
```

**Response:**

```json
{
  "prediction_id": "a3f7b2c1",
  "prediction": "LEGITIMATE",
  "fraud_probability": 0.294,
  "legitimate_probability": 0.706,
  "alert_level": "SAFE"
}
```

---

## 🔑 Key Features

- ✅ **Real-time predictions** — sub-second fraud verdict
- ✅ **Graph Neural Network** — detects fraud rings via card relationship patterns
- ✅ **Explainability** — feature importance breakdown per prediction
- ✅ **Cloud database** — every prediction logged to Snowflake
- ✅ **Production deployed** — live API + live dashboard
- ✅ **Professional UI** — dark theme with radar chart, gauge, risk breakdown
- ✅ **Transaction history** — session-based prediction tracking

---

## 📈 Dataset

- **Source:** [IEEE-CIS Fraud Detection — Kaggle](https://www.kaggle.com/competitions/ieee-fraud-detection)
- **Transactions:** 590,540
- **Features:** 434 raw → 31 selected behavioral features
- **Fraud Rate:** 3.5% (highly imbalanced, real-world distribution)
- **Identity Data:** 144,233 identity records merged on TransactionID

---

## 🏦 Why This Matters

Financial fraud costs the global economy **$485 billion annually**. Traditional rule-based systems miss complex fraud patterns that emerge from relationships between entities. FraudShield uses **Graph Neural Networks** to model the transaction graph — detecting fraud rings by analyzing connections between cards, merchants, and devices — not just individual transaction features. This is the approach used by JPMorgan, Stripe, and Razorpay in production.

---

## 👨‍💻 Author

**Varun Saji Nair**
- 📧 varunsajinair@gmail.com
- 🔗 [GitHub](https://github.com/varunsajinair)
- 💼 B.Tech CSE — 2nd Year
