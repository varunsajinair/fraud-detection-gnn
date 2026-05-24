from fastapi import FastAPI
from pydantic import BaseModel
import torch
import torch.nn.functional as F
from torch_geometric.nn import SAGEConv
import torch.nn as nn
import numpy as np

app = FastAPI(title="Fraud Detection GNN API", version="1.0")

# Define model architecture
class FraudGNN(nn.Module):
    def __init__(self, in_channels, hidden_channels, out_channels):
        super(FraudGNN, self).__init__()
        self.conv1 = SAGEConv(in_channels, hidden_channels)
        self.conv2 = SAGEConv(hidden_channels, hidden_channels)
        self.classifier = nn.Linear(hidden_channels, out_channels)
        self.dropout = nn.Dropout(p=0.5)
        
    def forward(self, x, edge_index):
        x = self.conv1(x, edge_index)
        x = F.relu(x)
        x = self.dropout(x)
        x = self.conv2(x, edge_index)
        x = F.relu(x)
        x = self.dropout(x)
        x = self.classifier(x)
        return x

# Load model and graph at startup
print("Loading model and graph...")
data = torch.load(
    r'C:\Users\varun\Desktop\fraud-gnn\data\graph_data.pt',
    map_location=torch.device('cpu'),
    weights_only=False
)
model = FraudGNN(in_channels=11, hidden_channels=64, out_channels=2)
model.load_state_dict(torch.load(
    r'C:\Users\varun\Desktop\fraud-gnn\models\fraud_gnn_model.pt',
    map_location=torch.device('cpu'),
    weights_only=False
))
model.eval()
print("✅ Model loaded!")

# Input schema
class Transaction(BaseModel):
    TransactionAmt: float
    C1: float
    C2: float
    C3: float
    C4: float
    C5: float
    V1: float
    V2: float
    V3: float
    V4: float
    V5: float

@app.get("/")
def home():
    return {"message": "Fraud Detection GNN API is running!"}

@app.post("/predict")
def predict(transaction: Transaction):
    # Create feature vector
    features = torch.tensor([[
        transaction.TransactionAmt,
        transaction.C1, transaction.C2, transaction.C3,
        transaction.C4, transaction.C5,
        transaction.V1, transaction.V2, transaction.V3,
        transaction.V4, transaction.V5
    ]], dtype=torch.float)
    
    # Use first node's edge connections
    edge_index = data.edge_index[:, :10]
    
    # Pad features to match graph size
    full_features = data.x.clone()
    full_features[0] = features[0]
    
    with torch.no_grad():
        out = model(full_features, data.edge_index)
        probs = torch.softmax(out, dim=1)
        fraud_prob = probs[0, 1].item()
        prediction = "FRAUD" if fraud_prob > 0.5 else "LEGITIMATE"
    
    return {
        "prediction": prediction,
        "fraud_probability": round(fraud_prob, 4),
        "legitimate_probability": round(1 - fraud_prob, 4),
        "top_fraud_signals": {
            "C2_address_count": transaction.C2,
            "C4_phone_count": transaction.C4,
            "TransactionAmt": transaction.TransactionAmt
        }
    }

@app.get("/health")
def health():
    return {"status": "healthy", "model": "FraudGNN", "version": "1.0"}