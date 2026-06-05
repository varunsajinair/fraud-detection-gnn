import streamlit as st
import requests
import random
import time
import pandas as pd
from datetime import datetime

st.set_page_config(
    page_title="FraudShield — Live Stream",
    page_icon="🛡️",
    layout="wide"
)

st.markdown("""
<style>
    .stApp { background-color: #0a0e1a; }
    .main .block-container { padding-top: 1rem; }
    hr { border-color: #1e3a5f !important; }
    p, label, .stMarkdown { color: #cbd5e1 !important; }
    h1, h2, h3 { color: white !important; }
    div[data-testid="stMetricValue"] { color: white !important; }
    div[data-testid="stMetricLabel"] { color: #94a3b8 !important; }
</style>
""", unsafe_allow_html=True)

st.markdown("""
<div style="background:linear-gradient(135deg,#0d1b2e,#1a2744);border-radius:16px;
     padding:24px 32px;margin-bottom:24px;border:1px solid #1e3a5f;">
    <h1 style="margin:0;color:white;font-size:28px;">Live Transaction Stream</h1>
    <p style="color:#64748b;margin:6px 0 0 0;font-size:13px;">
        Simulated real-time fraud detection feed
    </p>
</div>
""", unsafe_allow_html=True)

API_URL = "https://fraud-detection-gnn-production.up.railway.app/predict"

def generate_transaction():
    is_fraud_sim = random.random() < 0.5
    if is_fraud_sim:
        return {
            "TransactionAmt": round(random.uniform(1000, 8000), 2),
            "C1": random.randint(1, 3), "C2": random.randint(1, 3),
            "C3": 0.0,
            "C4": random.randint(0, 2), "C5": random.randint(0, 2),
            "C6": 1.0, "C7": 0.0, "C8": 0.0, "C9": 1.0, "C10": 0.0,
            "V1": 1.0, "V2": 1.0, "V3": 1.0, "V4": 1.0, "V5": 1.0,
            "V6": 1.0, "V7": 1.0, "V8": 1.0, "V9": 1.0, "V10": 1.0,
            "V11": 1.0, "V12": 1.0, "V13": 1.0, "V14": 1.0, "V15": 1.0,
            "V16": 1.0, "V17": 1.0, "V18": 1.0, "V19": 1.0, "V20": 1.0
        }
    else:
        return {
            "TransactionAmt": round(random.uniform(10, 500), 2),
            "C1": random.randint(1, 10), "C2": random.randint(1, 10),
            "C3": 0.0,
            "C4": random.randint(0, 5), "C5": random.randint(0, 3),
            "C6": 1.0, "C7": 0.0, "C8": 0.0, "C9": 1.0, "C10": 0.0,
            "V1": 1.0, "V2": 1.0, "V3": 1.0, "V4": 1.0, "V5": 1.0,
            "V6": 1.0, "V7": 1.0, "V8": 1.0, "V9": 1.0, "V10": 1.0,
            "V11": 1.0, "V12": 1.0, "V13": 1.0, "V14": 1.0, "V15": 1.0,
            "V16": 1.0, "V17": 1.0, "V18": 1.0, "V19": 1.0, "V20": 1.0
        }

if 'transactions' not in st.session_state:
    st.session_state.transactions = []
if 'running' not in st.session_state:
    st.session_state.running = False
if 'total' not in st.session_state:
    st.session_state.total = 0
if 'fraud_count' not in st.session_state:
    st.session_state.fraud_count = 0

col1, col2, col3, col4 = st.columns(4)
with col1:
    if st.button("Start Stream", use_container_width=True, type="primary"):
        st.session_state.running = True
with col2:
    if st.button("Stop Stream", use_container_width=True):
        st.session_state.running = False
with col3:
    speed = st.selectbox("Speed", ["Slow (2s)", "Normal (1s)", "Fast (0.5s)"], index=1)
with col4:
    if st.button("Clear", use_container_width=True):
        st.session_state.transactions = []
        st.session_state.total = 0
        st.session_state.fraud_count = 0

speed_map = {"Slow (2s)": 2.0, "Normal (1s)": 1.0, "Fast (0.5s)": 0.5}
delay = speed_map[speed]

st.divider()

m1, m2, m3, m4 = st.columns(4)
with m1: st.metric("Total Processed", st.session_state.total)
with m2: st.metric("Fraud Detected", st.session_state.fraud_count)
with m3: st.metric("Legitimate", st.session_state.total - st.session_state.fraud_count)
with m4:
    rate = (st.session_state.fraud_count / st.session_state.total * 100) if st.session_state.total > 0 else 0
    st.metric("Fraud Rate", f"{rate:.1f}%")

st.divider()

stream_placeholder = st.empty()

def render_transactions():
    html = ""
    for tx in reversed(st.session_state.transactions[-20:]):
        is_fraud = tx['prediction'] == 'FRAUD'
        bg = "#1a0505" if is_fraud else "#051a0f"
        border = "#dc2626" if is_fraud else "#059669"
        icon = "❌" if is_fraud else "✅"
        prob_color = "#dc2626" if is_fraud else "#059669"

        html += f"""
        <div style="background:{bg};border:1px solid {border};border-radius:8px;
                    padding:12px 16px;margin-bottom:6px;display:flex;
                    justify-content:space-between;align-items:center;">
            <div style="display:flex;align-items:center;gap:12px;">
                <span style="font-size:16px;">{icon}</span>
                <div>
                    <span style="color:white;font-weight:bold;font-size:13px;">{tx['id']}</span>
                    <span style="color:#64748b;font-size:11px;margin-left:8px;">{tx['time']}</span>
                </div>
            </div>
            <div style="display:flex;align-items:center;gap:24px;">
                <span style="color:#fbbf24;font-weight:bold;">${tx['amount']:,.2f}</span>
                <span style="color:{prob_color};font-size:12px;">{tx['prob']*100:.1f}% fraud</span>
                <span style="background:{border};color:white;padding:2px 10px;
                             border-radius:12px;font-size:11px;font-weight:bold;">{tx['prediction']}</span>
            </div>
        </div>
        """
    stream_placeholder.markdown(html, unsafe_allow_html=True)

render_transactions()

if st.session_state.running:
    for _ in range(50):
        if not st.session_state.running:
            break

        tx_data = generate_transaction()

        try:
            response = requests.post(API_URL, json=tx_data, timeout=10)
            result = response.json()

            tx_record = {
                'id': result.get('prediction_id', f"tx_{random.randint(1000,9999)}"),
                'amount': tx_data['TransactionAmt'],
                'prediction': result.get('prediction', 'UNKNOWN'),
                'prob': result.get('fraud_probability', 0),
                'alert': result.get('alert_level', 'LOW'),
                'time': datetime.now().strftime("%H:%M:%S")
            }

            st.session_state.transactions.append(tx_record)
            st.session_state.total += 1
            if tx_record['prediction'] == 'FRAUD':
                st.session_state.fraud_count += 1

            render_transactions()

            with m1: st.metric("Total Processed", st.session_state.total)
            with m2: st.metric("Fraud Detected", st.session_state.fraud_count)
            with m3: st.metric("Legitimate", st.session_state.total - st.session_state.fraud_count)
            with m4:
                rate = (st.session_state.fraud_count / st.session_state.total * 100)
                st.metric("Fraud Rate", f"{rate:.1f}%")

        except Exception as e:
            st.error(f"API error: {e}")
            break

        time.sleep(delay)

    st.session_state.running = False
    st.rerun()