# Fraud Detection using Spatial-Temporal GNN

A Graph Neural Network based real-time fraud detection system using 
heterogeneous graphs with temporal encoding.

## Architecture
- **Graph Layer**: PyTorch Geometric (GraphSAGE)
- **Temporal Encoder**: LSTM
- **Explainability**: GNNExplainer
- **Database**: Snowflake + IBM DB2
- **Serving**: FastAPI
- **Dashboard**: Streamlit

## Dataset
IEEE-CIS Fraud Detection Dataset (590K transactions)

## Setup
```bash
conda activate fraudgnn
pip install -r requirements.txt
```

## Project Status
🚧 In Progress