from fastapi import FastAPI
from pydantic import BaseModel
import numpy as np
import pickle
import snowflake.connector
from datetime import datetime
import uuid
import os

app = FastAPI(title="FraudShield API", version="2.0")

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

print("Loading models...")
with open(os.path.join(BASE_DIR, 'models', 'fraud_classifier.pkl'), 'rb') as f:
    classifier = pickle.load(f)
with open(os.path.join(BASE_DIR, 'models', 'scaler.pkl'), 'rb') as f:
    scaler = pickle.load(f)
with open(os.path.join(BASE_DIR, 'models', 'feature_cols.pkl'), 'rb') as f:
    feature_cols = pickle.load(f)

print(f"✅ Models loaded! Features: {len(feature_cols)}")

def get_snowflake_conn():
    return snowflake.connector.connect(
        user=os.getenv('SNOWFLAKE_USER'),
        password=os.getenv('SNOWFLAKE_PASSWORD'),
        account=os.getenv('SNOWFLAKE_ACCOUNT', 'sxkobdu-fw40635'),
        warehouse='COMPUTE_WH',
        database='FRAUDSHIELD',
        schema='FRAUD_DETECTION'
    )

def log_to_snowflake(prediction_id, amount, C1, C2, C4, C5, fraud_prob, prediction, alert):
    try:
        conn = get_snowflake_conn()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO FRAUD_PREDICTIONS 
            (PREDICTION_ID, TIMESTAMP, TRANSACTION_AMOUNT, C1, C2, C4, C5,
             FRAUD_PROBABILITY, PREDICTION, ALERT_LEVEL)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, (prediction_id, datetime.now(), amount, C1, C2, C4, C5,
              fraud_prob, prediction, alert))
        conn.commit()
        cursor.close()
        conn.close()
        print(f"✅ Logged to Snowflake: {prediction_id}")
    except Exception as e:
        print(f"⚠️ Snowflake logging failed: {e}")

class Transaction(BaseModel):
    TransactionAmt: float
    C1: float = 1.0
    C2: float = 1.0
    C3: float = 0.0
    C4: float = 0.0
    C5: float = 0.0
    C6: float = 1.0
    C7: float = 0.0
    C8: float = 0.0
    C9: float = 1.0
    C10: float = 0.0
    V1: float = 1.0
    V2: float = 1.0
    V3: float = 1.0
    V4: float = 1.0
    V5: float = 1.0
    V6: float = 1.0
    V7: float = 1.0
    V8: float = 1.0
    V9: float = 1.0
    V10: float = 1.0
    V11: float = 1.0
    V12: float = 1.0
    V13: float = 1.0
    V14: float = 1.0
    V15: float = 1.0
    V16: float = 1.0
    V17: float = 1.0
    V18: float = 1.0
    V19: float = 1.0
    V20: float = 1.0

@app.get("/")
def home():
    return {"message": "FraudShield API is running!"}

@app.post("/predict")
def predict(transaction: Transaction):
    features = np.array([[
        transaction.TransactionAmt,
        transaction.C1, transaction.C2, transaction.C3,
        transaction.C4, transaction.C5, transaction.C6,
        transaction.C7, transaction.C8, transaction.C9, transaction.C10,
        transaction.V1, transaction.V2, transaction.V3, transaction.V4,
        transaction.V5, transaction.V6, transaction.V7, transaction.V8,
        transaction.V9, transaction.V10, transaction.V11, transaction.V12,
        transaction.V13, transaction.V14, transaction.V15, transaction.V16,
        transaction.V17, transaction.V18, transaction.V19, transaction.V20
    ]])
    
    scaled = scaler.transform(features)
    fraud_prob = classifier.predict_proba(scaled)[0][1]
    prediction = "FRAUD" if fraud_prob > 0.5 else "LEGITIMATE"
    
    if fraud_prob < 0.3:
        alert = "SAFE"
    elif fraud_prob < 0.5:
        alert = "LOW RISK"
    elif fraud_prob < 0.75:
        alert = "HIGH RISK"
    else:
        alert = "CRITICAL"
    
    prediction_id = str(uuid.uuid4())[:8]
    
    log_to_snowflake(
        prediction_id,
        transaction.TransactionAmt,
        transaction.C1, transaction.C2,
        transaction.C4, transaction.C5,
        round(float(fraud_prob), 4),
        prediction, alert
    )
    
    return {
        "prediction_id": prediction_id,
        "prediction": prediction,
        "fraud_probability": round(float(fraud_prob), 4),
        "legitimate_probability": round(float(1 - fraud_prob), 4),
        "alert_level": alert
    }

@app.get("/health")
def health():
    return {"status": "healthy", "model": "RandomForest", "features": len(feature_cols)}