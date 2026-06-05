import streamlit as st
import requests
import pandas as pd
import time
import io
from datetime import datetime

st.set_page_config(
    page_title="FraudShield — Batch Upload",
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
    .stButton > button {
        background: linear-gradient(135deg, #1d4ed8, #1e40af) !important;
        color: white !important;
        border: none !important;
        border-radius: 10px !important;
        font-weight: 700 !important;
        width: 100% !important;
    }
    .stDownloadButton > button {
        background: linear-gradient(135deg, #064e3b, #059669) !important;
        color: white !important;
        border: none !important;
        border-radius: 10px !important;
        font-weight: 700 !important;
        width: 100% !important;
    }
</style>
""", unsafe_allow_html=True)

st.markdown("""
<div style="background:linear-gradient(135deg,#0d1b2e,#1a2744);border-radius:16px;
     padding:24px 32px;margin-bottom:24px;border:1px solid #1e3a5f;">
    <h1 style="margin:0;color:white;font-size:28px;">Batch Transaction Screening</h1>
    <p style="color:#64748b;margin:6px 0 0 0;font-size:13px;">
        Upload a CSV of transactions and get fraud predictions for all of them
    </p>
</div>
""", unsafe_allow_html=True)

col1, col2 = st.columns([1.5, 1])

with col1:
    st.markdown("#### How to use")
    st.markdown("""
    1. Download the sample CSV template below
    2. Fill in your transaction data
    3. Upload the CSV file
    4. Click Run Batch Analysis
    5. Download results with fraud predictions
    """)

    sample_data = pd.DataFrame({
        'TransactionAmt': [150.0, 50.0, 2000.0, 75.0, 500.0, 37.0, 890.0, 120.0, 4500.0, 200.0],
        'C1': [1, 6, 3, 1, 2, 0, 5, 1, 8, 1],
        'C2': [1, 2, 5, 1, 3, 1, 7, 2, 9, 1],
        'C4': [0, 1, 2, 0, 0, 1, 3, 0, 4, 0],
        'C5': [0, 0, 1, 0, 0, 0, 2, 0, 3, 0]
    })

    st.download_button(
        label="Download Sample CSV Template",
        data=sample_data.to_csv(index=False),
        file_name="fraudshield_template.csv",
        mime="text/csv",
        use_container_width=True
    )

with col2:
    st.markdown("#### Required Columns")
    st.markdown("""
    <div style="background:#0d1b2e;border:1px solid #1e3a5f;border-radius:10px;padding:16px;">
    <table style="width:100%;color:#cbd5e1;font-size:13px;">
        <tr><td style="color:#94a3b8;">Column</td><td style="color:#94a3b8;">Description</td></tr>
        <tr><td><b>TransactionAmt</b></td><td>Amount in USD</td></tr>
        <tr><td><b>C1</b></td><td>Card address count</td></tr>
        <tr><td><b>C2</b></td><td>Card usage pattern</td></tr>
        <tr><td><b>C4</b></td><td>Phone numbers linked</td></tr>
        <tr><td><b>C5</b></td><td>Email accounts linked</td></tr>
    </table>
    </div>
    """, unsafe_allow_html=True)

st.divider()

uploaded_file = st.file_uploader(
    "Upload your CSV file",
    type=['csv'],
    help="CSV must have columns: TransactionAmt, C1, C2, C4, C5"
)

if uploaded_file:
    df = pd.read_csv(uploaded_file)

    st.markdown(f"#### Preview — {len(df)} transactions loaded")
    st.dataframe(df.head(10), use_container_width=True, hide_index=True)

    required = ['TransactionAmt', 'C1', 'C2', 'C4', 'C5']
    missing = [c for c in required if c not in df.columns]

    if missing:
        st.error(f"Missing columns: {missing}")
        st.stop()

    st.success(f"{len(df)} transactions ready for screening")

    if st.button("Run Batch Fraud Analysis", type="primary"):

        results = []
        progress = st.progress(0)
        status = st.empty()

        for i, row in df.iterrows():
            status.markdown(f"<p style='color:#64748b;font-size:13px;'>Analyzing transaction {i+1} of {len(df)}...</p>", unsafe_allow_html=True)

            payload = {
                "TransactionAmt": float(row['TransactionAmt']),
                "C1": float(row.get('C1', 1)),
                "C2": float(row.get('C2', 1)),
                "C3": 0.0,
                "C4": float(row.get('C4', 0)),
                "C5": float(row.get('C5', 0)),
                "C6": 1.0, "C7": 0.0, "C8": 0.0, "C9": 1.0, "C10": 0.0,
                "V1": 1.0, "V2": 1.0, "V3": 1.0, "V4": 1.0, "V5": 1.0,
                "V6": 1.0, "V7": 1.0, "V8": 1.0, "V9": 1.0, "V10": 1.0,
                "V11": 1.0, "V12": 1.0, "V13": 1.0, "V14": 1.0, "V15": 1.0,
                "V16": 1.0, "V17": 1.0, "V18": 1.0, "V19": 1.0, "V20": 1.0
            }

            try:
                response = requests.post(
                    "https://fraud-detection-gnn-production.up.railway.app/predict",
                    json=payload,
                    timeout=60
                )
                result = response.json()
                results.append({
                    'TransactionAmt': row['TransactionAmt'],
                    'C1': row['C1'], 'C2': row['C2'],
                    'C4': row['C4'], 'C5': row['C5'],
                    'Prediction': result['prediction'],
                    'Fraud_Probability': f"{result['fraud_probability']*100:.1f}%",
                    'Alert_Level': result['alert_level'],
                    'Prediction_ID': result.get('prediction_id', 'N/A')
                })
            except Exception as e:
                results.append({
                    'TransactionAmt': row['TransactionAmt'],
                    'C1': row['C1'], 'C2': row['C2'],
                    'C4': row['C4'], 'C5': row['C5'],
                    'Prediction': 'ERROR',
                    'Fraud_Probability': 'N/A',
                    'Alert_Level': 'N/A',
                    'Prediction_ID': str(e)[:30]
                })

            time.sleep(0.8)
            progress.progress((i+1) / len(df))

        status.empty()
        progress.empty()

        results_df = pd.DataFrame(results)

        fraud_count = len(results_df[results_df['Prediction'] == 'FRAUD'])
        legit_count = len(results_df[results_df['Prediction'] == 'LEGITIMATE'])

        st.divider()
        st.markdown("### Batch Results")

        m1, m2, m3, m4 = st.columns(4)
        with m1: st.metric("Total Screened", len(results_df))
        with m2: st.metric("Fraud Detected", fraud_count)
        with m3: st.metric("Legitimate", legit_count)
        with m4: st.metric("Fraud Rate", f"{fraud_count/len(results_df)*100:.1f}%")

        st.divider()

        def highlight_row(row):
            if row['Prediction'] == 'FRAUD':
                return ['background-color: #450a0a; color: #fca5a5'] * len(row)
            elif row['Prediction'] == 'LEGITIMATE':
                return ['background-color: #064e3b; color: #6ee7b7'] * len(row)
            else:
                return ['background-color: #1e3a5f; color: #94a3b8'] * len(row)

        st.dataframe(
            results_df.style.apply(highlight_row, axis=1),
            use_container_width=True,
            hide_index=True
        )

        st.download_button(
            label="Download Results CSV",
            data=results_df.to_csv(index=False),
            file_name=f"fraudshield_batch_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
            mime="text/csv",
            use_container_width=True
        )