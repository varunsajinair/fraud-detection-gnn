<div align="center">

# 🛡️ FraudShield AI

### Production-Grade Financial Crime Detection Platform

[![Python](https://img.shields.io/badge/Python-3.10-blue?style=for-the-badge&logo=python)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.100+-green?style=for-the-badge&logo=fastapi)](https://fastapi.tiangolo.com)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.28+-red?style=for-the-badge&logo=streamlit)](https://streamlit.io)
[![Snowflake](https://img.shields.io/badge/Snowflake-Data_Warehouse-29B5E8?style=for-the-badge&logo=snowflake)](https://snowflake.com)
[![Docker](https://img.shields.io/badge/Docker-Containerized-2496ED?style=for-the-badge&logo=docker)](https://docker.com)
[![Railway](https://img.shields.io/badge/Railway-Deployed-0B0D0E?style=for-the-badge&logo=railway)](https://railway.app)

**Trained on 590,000 IEEE-CIS transactions | GraphSAGE GNN | Real-time Detection | AML | XAI**

[🚀 Live Demo](https://fraudshield-varun.streamlit.app) • [📡 API Docs](https://fraud-detection-gnn-production.up.railway.app/docs) • [📊 Dashboard](https://fraudshield-varun.streamlit.app)

</div>

---

## 🎯 What is FraudShield?

FraudShield is a **production-grade financial crime detection platform** built with GraphSAGE Graph Neural Networks. Unlike traditional ML approaches that treat transactions independently, FraudShield learns from **relationships between transactions** — detecting fraud rings, coordinated attacks, and money laundering patterns that standard models miss.

> 💡 The U.S. Treasury recovered $4B+ in fraud in 2024 using ML systems. FraudShield demonstrates exactly how these systems work.

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     FraudShield Platform                     │
├──────────────┬────────────────┬─────────────────────────────┤
│  GraphSAGE   │  Random Forest │      FastAPI (Railway)       │
│     GNN      │   Classifier   │    REST API + /predict       │
├──────────────┴────────────────┴─────────────────────────────┤
│                Snowflake Data Warehouse                      │
│           (All predictions logged in real-time)             │
├─────────────────────────────────────────────────────────────┤
│               Streamlit Dashboard (9 Pages)                  │
│  Analytics │ Graph │ Batch │ Email │ Stream │ AML │ XAI      │
└─────────────────────────────────────────────────────────────┘
```

---

## ✨ Features

| Feature | Description | Tech |
|---------|-------------|------|
| 🧠 **GraphSAGE GNN** | Graph Neural Network trained on 590K transactions | PyTorch Geometric |
| ⚡ **Real-time API** | Sub-100ms fraud predictions via REST API | FastAPI + Railway |
| 📊 **Analytics Dashboard** | Live charts from Snowflake predictions | Streamlit + Plotly |
| 🕸️ **Graph Visualization** | Interactive fraud network with ring detection | PyVis + NetworkX |
| 📦 **Batch Processing** | Upload CSV, screen 1000s of transactions at once | Pandas + FastAPI |
| 📧 **Email Alerts** | Auto-send fraud alerts like real banking systems | SendGrid |
| ⚡ **Live Stream** | Real-time transaction ticker with AI predictions | Streamlit + Requests |
| 📡 **Model Monitoring** | PSI drift detection, model health tracking | Numpy + Plotly |
| 🧠 **Explainable AI** | Feature contributions per prediction (GDPR Art.22) | Custom XAI Engine |
| ⚖️ **Model Comparison** | GNN vs RF vs XGBoost vs LR — radar charts | Plotly |
| 🏦 **AML Detection** | Money laundering pattern detection + SAR generator | Custom AML Engine |
| 🐳 **Docker** | Fully containerized with docker-compose | Docker |
| 📋 **PDF Reports** | Downloadable compliance reports for every prediction | FPDF2 |

---

## 📸 Screenshots

### 🏠 Main Dashboard
![Dashboard](screenshots/01_dashboard.png)

### 📊 Analytics
![Analytics](screenshots/02_analytics.png)

### 📦 Batch Upload
![Batch](screenshots/03_batch.png)

### 🕸️ Graph Visualization
![Graph](screenshots/04_graph.png)

### 📧 Email Alerts
![Email](screenshots/05_email.png)

### ⚡ Live Transaction Stream
![Stream](screenshots/06_stream.png)

### 📡 Model Monitoring
![Monitoring 1](screenshots/07_monitoring1.png)
![Monitoring 2](screenshots/08_monitoring2.png)

### 🧠 Explainable AI (XAI)
![XAI 1](screenshots/09_xai1.png)
![XAI 2](screenshots/10_xai2.png)

### ⚖️ Model Comparison
![Comparison 1](screenshots/11_comparison1.png)
![Comparison 2](screenshots/12_comparison2.png)
![Comparison 3](screenshots/13_comparison3.png)

### 🏦 AML Detection
![AML 1](screenshots/14_aml1.png)
![AML 2](screenshots/15_aml2.png)
![AML 3](screenshots/16_aml3.png)

---

## 🚀 Quick Start

### Option 1 — Docker (Recommended)

```bash
git clone https://github.com/varunsajinair/fraud-detection-gnn
cd fraud-detection-gnn
cp .env.example .env
# Fill in your credentials in .env
docker-compose up
```

### Option 2 — Local Setup

```bash
# Clone repo
git clone https://github.com/varunsajinair/fraud-detection-gnn
cd fraud-detection-gnn

# Install API dependencies
pip install -r requirements-api.txt

# Run API
cd src
uvicorn app:app --reload --port 8000

# Run Dashboard (new terminal)
cd dashboard
streamlit run dashboard.py
```

---

## 🧠 Model Performance

| Model | Accuracy | F1 Score | AUC-ROC | Inference |
|-------|----------|----------|---------|-----------|
| **GraphSAGE GNN** ⭐ | **97.8%** | **91.8%** | **97.1%** | 12ms |
| Random Forest | 96.4% | 87.9% | 94.8% | 3ms |
| XGBoost | 96.1% | 86.8% | 93.9% | 2ms |
| Logistic Regression | 91.2% | 68.8% | 86.2% | 1ms |

> GraphSAGE GNN outperforms all baselines by learning from **transaction relationships and graph structure** — not just individual transaction features.

---

## 📡 API Reference

**Base URL:** `https://fraud-detection-gnn-production.up.railway.app`

### POST `/predict`

```json
{
  "TransactionAmt": 5000.00,
  "ProductCD": "W",
  "card4": "visa",
  "card6": "credit",
  "P_emaildomain": "gmail.com",
  "R_emaildomain": "anonymous.com",
  "C1": 1, "C2": 1, "C4": 1, "C5": 0,
  "C6": 1, "C7": 0, "C8": 1, "C9": 0,
  "C10": 0, "C11": 1, "C12": 0, "C13": 2,
  "C14": 1, "D1": 5, "D2": 3,
  "M1": "T", "M2": "T", "M3": "T", "M4": "M0",
  "V1": 0.5, "V2": 0.3, "V3": 0.8
}
```

**Response:**

```json
{
  "prediction_id": "a1b2c3d4",
  "prediction": "FRAUD",
  "fraud_probability": 0.87,
  "legitimate_probability": 0.13,
  "alert_level": "HIGH RISK"
}
```

### GET `/health`

```json
{
  "status": "healthy",
  "model": "RandomForest",
  "features": 31
}
```

---

## 🏦 AML Detection

FraudShield includes a full **Anti-Money Laundering (AML)** detection module that goes beyond single transaction fraud detection:

| Pattern | Description | Risk |
|---------|-------------|------|
| **Structuring (Smurfing)** | Breaking large amounts into sub-$10K transactions | HIGH |
| **Layering** | Rapid movement through multiple accounts | CRITICAL |
| **Integration** | Reintroducing laundered money as legitimate | HIGH |
| **Round Tripping** | Money sent abroad returned as foreign investment | MEDIUM |
| **Rapid Movement** | Funds moving through accounts within hours | HIGH |

> Includes automated **SAR (Suspicious Activity Report)** generation — the same reports banks file with FinCEN.

---

## 📡 Model Monitoring

FraudShield tracks model health in production using industry-standard metrics:

- **PSI (Population Stability Index)** — detects data drift
  - PSI < 0.1 → Stable ✅
  - PSI 0.1–0.2 → Minor drift ⚠️
  - PSI > 0.2 → Major drift 🚨 (retraining recommended)
- **Fraud rate over time** — detects concept drift
- **Model confidence tracking** — monitors prediction quality
- **Alert level distribution** — tracks risk tier changes

---

## 🧠 Explainable AI (XAI)

Every fraud prediction includes a full explanation of **why** the transaction was flagged:

- **Feature contribution bars** — which features pushed toward fraud vs legitimate
- **Fraud probability gauge** — visual risk score
- **Global feature importance** — what matters most across all fraud predictions
- **GDPR Article 22 compliant** — banks must explain automated decisions

---

## 🗂️ Project Structure

```
fraud-detection-gnn/
├── src/
│   ├── app.py                  # FastAPI application
│   └── report_generator.py     # PDF compliance reports
├── dashboard/
│   ├── dashboard.py            # Main Streamlit app
│   ├── .streamlit/
│   │   └── secrets.toml        # Local secrets (gitignored)
│   └── pages/
│       ├── 01_Analytics.py
│       ├── 02_Batch_Upload.py
│       ├── 03_Graph_Visualization.py
│       ├── 04_Email_Alerts.py
│       ├── 05_Live_Stream.py
│       ├── 06_Model_Monitoring.py
│       ├── 07_Explainability.py
│       ├── 08_Model_Comparison.py
│       └── 09_AML_Detection.py
├── models/                     # Trained model files
├── notebooks/                  # Training notebooks
├── screenshots/                # Dashboard screenshots
├── Dockerfile
├── docker-compose.yml
├── .env.example
├── Procfile
├── railway.json
├── requirements.txt
└── requirements-api.txt
```

---

## 🔧 Environment Variables

```env
SNOWFLAKE_USER=your_snowflake_username
SNOWFLAKE_PASSWORD=your_snowflake_password
SNOWFLAKE_ACCOUNT=your_snowflake_account
SENDGRID_API_KEY=your_sendgrid_api_key
```

---

## 🌐 Deployment

| Service | Platform | URL |
|---------|----------|-----|
| FastAPI Backend | Railway | https://fraud-detection-gnn-production.up.railway.app |
| Streamlit Dashboard | Streamlit Cloud | https://fraudshield-varun.streamlit.app |
| Data Warehouse | Snowflake | FRAUDSHIELD.FRAUD_DETECTION.FRAUD_PREDICTIONS |

---

## 📚 Dataset

- **Source:** IEEE-CIS Fraud Detection (Kaggle)
- **Size:** 590,540 transactions
- **Features:** 434 raw features → 31 engineered features
- **Class imbalance:** 3.5% fraud, 96.5% legitimate
- **Handling:** Class weights + graph-based oversampling

---

## 💼 Resume Line

> Built FraudShield — production-grade financial crime detection platform using GraphSAGE GNN trained on 590K IEEE-CIS transactions. Features real-time fraud detection, AML pattern analysis with SAR generation, explainable AI (GDPR-compliant XAI), model monitoring with PSI drift detection, automated email alerting, live transaction streaming, and model comparison dashboard. Deployed on Railway + Streamlit Cloud with Snowflake as prediction warehouse. Fully containerized with Docker.

---

## 🙏 Acknowledgements

- IEEE-CIS Fraud Detection Dataset (Kaggle)
- PyTorch Geometric for GraphSAGE implementation
- Streamlit for the dashboard framework
- Snowflake for the data warehouse
- Railway for API deployment
- SendGrid for email alerts

---

<div align="center">

**Built with ❤️ by Varun Sajinair**

⭐ Star this repo if you found it useful!

</div>
