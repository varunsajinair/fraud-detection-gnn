import streamlit as st
import requests
import plotly.graph_objects as go
import pandas as pd
import numpy as np
import time
from datetime import datetime
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from src.report_generator import generate_fraud_report

st.set_page_config(
    page_title="FraudShield — AI Fraud Detection",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="collapsed"
)

st.markdown("""
<style>
    .stApp { background-color: #0a0e1a; }
    .main .block-container { padding-top: 1rem; }

    .header-container {
        background: linear-gradient(135deg, #0d1b2e 0%, #1a2744 100%);
        border-radius: 16px;
        padding: 24px 32px;
        margin-bottom: 24px;
        border: 1px solid #1e3a5f;
    }

    .fraud-verdict {
        background: linear-gradient(135deg, #7f1d1d, #dc2626);
        border-radius: 16px;
        padding: 28px;
        text-align: center;
        color: white;
        font-size: 28px;
        font-weight: 800;
        letter-spacing: 1px;
        border: 1px solid #ef4444;
        margin-bottom: 20px;
        box-shadow: 0 0 30px rgba(220, 38, 38, 0.3);
    }
    .legit-verdict {
        background: linear-gradient(135deg, #064e3b, #059669);
        border-radius: 16px;
        padding: 28px;
        text-align: center;
        color: white;
        font-size: 28px;
        font-weight: 800;
        letter-spacing: 1px;
        border: 1px solid #10b981;
        margin-bottom: 20px;
        box-shadow: 0 0 30px rgba(16, 185, 129, 0.3);
    }

    .badge-safe { background: #064e3b; color: #34d399; padding: 6px 16px; border-radius: 20px; font-weight: 600; font-size: 14px; border: 1px solid #10b981; }
    .badge-low { background: #1e3a5f; color: #60a5fa; padding: 6px 16px; border-radius: 20px; font-weight: 600; font-size: 14px; border: 1px solid #3b82f6; }
    .badge-high { background: #451a03; color: #fb923c; padding: 6px 16px; border-radius: 20px; font-weight: 600; font-size: 14px; border: 1px solid #f97316; }
    .badge-critical { background: #450a0a; color: #f87171; padding: 6px 16px; border-radius: 20px; font-weight: 600; font-size: 14px; border: 1px solid #ef4444; }

    div[data-testid="stNumberInput"] input {
        background-color: #0d1b2e !important;
        color: white !important;
        border: 1px solid #1e3a5f !important;
    }
    div[data-testid="stNumberInput"] {
        background-color: #0d1b2e !important;
    }

    .stButton > button {
        background: linear-gradient(135deg, #1d4ed8, #1e40af) !important;
        color: white !important;
        border: none !important;
        border-radius: 10px !important;
        padding: 16px !important;
        font-size: 18px !important;
        font-weight: 700 !important;
        width: 100% !important;
        letter-spacing: 0.5px !important;
    }
    .stButton > button:hover {
        background: linear-gradient(135deg, #2563eb, #1d4ed8) !important;
        box-shadow: 0 0 20px rgba(37, 99, 235, 0.5) !important;
    }

    .stDownloadButton > button {
        background: linear-gradient(135deg, #064e3b, #059669) !important;
        color: white !important;
        border: none !important;
        border-radius: 10px !important;
        padding: 12px !important;
        font-size: 15px !important;
        font-weight: 600 !important;
        width: 100% !important;
    }

    .section-header {
        color: #94a3b8;
        font-size: 11px;
        font-weight: 600;
        letter-spacing: 2px;
        text-transform: uppercase;
        margin-bottom: 12px;
        margin-top: 20px;
    }

    hr { border-color: #1e3a5f !important; }
    p, label, .stMarkdown { color: #cbd5e1 !important; }
    h1, h2, h3 { color: white !important; }
    div[data-testid="stMetricValue"] { color: white !important; }
    div[data-testid="stMetricLabel"] { color: #94a3b8 !important; }
    .stDataFrame { background: #0d1b2e !important; }
    thead tr th { background: #1e3a5f !important; color: white !important; }
    tbody tr td { background: #0d1b2e !important; color: #cbd5e1 !important; }
</style>
""", unsafe_allow_html=True)

if 'history' not in st.session_state:
    st.session_state.history = []

st.markdown("""
<div class="header-container">
    <div style="display:flex; justify-content:space-between; align-items:center;">
        <div>
            <h1 style="margin:0; font-size:28px; color:white;">🛡️ FraudShield</h1>
            <p style="margin:4px 0 0 0; color:#64748b; font-size:14px;">
                Real-time AI Fraud Detection &nbsp;·&nbsp; GraphSAGE GNN + Random Forest
            </p>
        </div>
        <div style="text-align:right;">
            <p style="margin:0; color:#34d399; font-size:13px; font-weight:600;">● SYSTEM ONLINE</p>
            <p style="margin:4px 0 0 0; color:#475569; font-size:12px;">IEEE-CIS Dataset · 590K Transactions</p>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

total = len(st.session_state.history)
fraud_count = sum(1 for h in st.session_state.history if h['prediction'] == 'FRAUD')
legit_count = total - fraud_count
avg_prob = np.mean([h['fraud_prob'] for h in st.session_state.history]) * 100 if total > 0 else 0

s1, s2, s3, s4 = st.columns(4)
with s1: st.metric("Total Analyzed", total)
with s2: st.metric("Fraud Detected", fraud_count)
with s3: st.metric("Legitimate", legit_count)
with s4: st.metric("Avg Risk Score", f"{avg_prob:.1f}%")

st.divider()

left, right = st.columns([1, 1.6])

with left:
    st.markdown('<div class="section-header">Transaction Input</div>', unsafe_allow_html=True)

    amount = st.number_input(
        "Transaction Amount ($)",
        min_value=0.1, max_value=50000.0,
        value=150.0, step=1.0,
        help="Transaction amount in USD"
    )

    st.markdown('<div class="section-header">Card Behavior Metrics</div>', unsafe_allow_html=True)
    st.caption("Behavioral signals from the card network system")

    col_a, col_b = st.columns(2)
    with col_a:
        C1 = st.number_input("C1 · Address Count", min_value=0.0, max_value=100.0, value=1.0, step=1.0,
            help="Addresses linked to card. Normal: 1-2 | Risk: >4")
        C4 = st.number_input("C4 · Phone Links", min_value=0.0, max_value=50.0, value=0.0, step=1.0,
            help="Phone numbers linked. Normal: 0 | Risk: >1")
    with col_b:
        C2 = st.number_input("C2 · Usage Pattern", min_value=0.0, max_value=100.0, value=1.0, step=1.0,
            help="Card usage frequency. Normal: 1-3 | Risk: >5")
        C5 = st.number_input("C5 · Email Count", min_value=0.0, max_value=20.0, value=0.0, step=1.0,
            help="Email accounts linked. Normal: 0-1 | Risk: >2")

    st.divider()
    st.markdown('<div class="section-header">Quick Test Cases</div>', unsafe_allow_html=True)

    tc1, tc2 = st.columns(2)
    with tc1:
        st.markdown("""
        <div style="background:#064e3b; border:1px solid #10b981; border-radius:8px; padding:10px;">
            <p style="color:#34d399; font-weight:600; margin:0; font-size:13px;">LEGITIMATE</p>
            <p style="color:#6ee7b7; margin:4px 0 0 0; font-size:12px;">
            Amount: $150<br>C1=1, C2=1<br>C4=0, C5=0
            </p>
        </div>
        """, unsafe_allow_html=True)
    with tc2:
        st.markdown("""
        <div style="background:#450a0a; border:1px solid #ef4444; border-radius:8px; padding:10px;">
            <p style="color:#f87171; font-weight:600; margin:0; font-size:13px;">FRAUD</p>
            <p style="color:#fca5a5; margin:4px 0 0 0; font-size:12px;">
            Amount: $50<br>C1=6, C2=2<br>C4=1, C5=0
            </p>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    predict_btn = st.button("Analyze Transaction", type="primary")

    st.divider()
    st.markdown('<div class="section-header">Model Information</div>', unsafe_allow_html=True)
    st.markdown("""
    <div style="background:#0d1b2e; border:1px solid #1e3a5f; border-radius:10px; padding:14px;">
        <table style="width:100%; color:#94a3b8; font-size:12px; border-collapse:collapse;">
            <tr><td style="padding:4px 0;">Architecture</td><td style="color:white; text-align:right;">GNN + Random Forest</td></tr>
            <tr><td style="padding:4px 0;">Dataset</td><td style="color:white; text-align:right;">IEEE-CIS Fraud</td></tr>
            <tr><td style="padding:4px 0;">Training Size</td><td style="color:white; text-align:right;">590,000 txns</td></tr>
            <tr><td style="padding:4px 0;">Features</td><td style="color:white; text-align:right;">31 behavioral</td></tr>
            <tr><td style="padding:4px 0;">Accuracy</td><td style="color:#34d399; text-align:right;">84%</td></tr>
            <tr><td style="padding:4px 0;">Fraud Recall</td><td style="color:#34d399; text-align:right;">67%</td></tr>
        </table>
    </div>
    """, unsafe_allow_html=True)

with right:
    if predict_btn:
        start_time = time.time()

        payload = {
            "TransactionAmt": amount,
            "C1": C1, "C2": C2, "C3": 0.0,
            "C4": C4, "C5": C5, "C6": 1.0,
            "C7": 0.0, "C8": 0.0, "C9": 1.0, "C10": 0.0,
            "V1": 1.0, "V2": 1.0, "V3": 1.0, "V4": 1.0, "V5": 1.0,
            "V6": 1.0, "V7": 1.0, "V8": 1.0, "V9": 1.0, "V10": 1.0,
            "V11": 1.0, "V12": 1.0, "V13": 1.0, "V14": 1.0, "V15": 1.0,
            "V16": 1.0, "V17": 1.0, "V18": 1.0, "V19": 1.0, "V20": 1.0
        }

        try:
            response = requests.post(
                "https://fraud-detection-gnn-production.up.railway.app/predict",
                json=payload
            )
            result = response.json()
            response_time = (time.time() - start_time) * 1000

            fraud_prob = result['fraud_probability']
            prediction = result['prediction']

            st.session_state.history.append({
                'time': datetime.now().strftime("%H:%M:%S"),
                'amount': amount,
                'C1': C1, 'C2': C2, 'C4': C4,
                'fraud_prob': fraud_prob,
                'prediction': prediction
            })

            if fraud_prob < 0.3:
                alert = "SAFE"
                alert_class = "badge-safe"
                alert_emoji = "🟢"
            elif fraud_prob < 0.5:
                alert = "LOW RISK"
                alert_class = "badge-low"
                alert_emoji = "🔵"
            elif fraud_prob < 0.75:
                alert = "HIGH RISK"
                alert_class = "badge-high"
                alert_emoji = "🟠"
            else:
                alert = "CRITICAL"
                alert_class = "badge-critical"
                alert_emoji = "🔴"

            if prediction == "FRAUD":
                st.markdown('<div class="fraud-verdict">FRAUDULENT TRANSACTION DETECTED</div>',
                    unsafe_allow_html=True)
            else:
                st.markdown('<div class="legit-verdict">LEGITIMATE TRANSACTION</div>',
                    unsafe_allow_html=True)

            m1, m2, m3, m4 = st.columns(4)
            with m1: st.metric("Fraud Risk", f"{fraud_prob*100:.1f}%")
            with m2: st.metric("Amount", f"${amount:,.0f}")
            with m3: st.markdown(f'<br><span class="{alert_class}">{alert_emoji} {alert}</span>',
                           unsafe_allow_html=True)
            with m4: st.metric("Response", f"{response_time:.0f}ms")

            st.divider()

            ch1, ch2 = st.columns(2)

            with ch1:
                color = "#ef4444" if fraud_prob > 0.5 else "#10b981"
                fig = go.Figure(go.Indicator(
                    mode="gauge+number",
                    value=fraud_prob * 100,
                    title={'text': "Risk Score", 'font': {'color': 'white', 'size': 16}},
                    number={'font': {'color': 'white', 'size': 36}, 'suffix': '%'},
                    gauge={
                        'axis': {'range': [0, 100], 'tickcolor': '#475569',
                                'tickfont': {'color': '#475569'}},
                        'bar': {'color': color, 'thickness': 0.3},
                        'bgcolor': '#0d1b2e',
                        'bordercolor': '#1e3a5f',
                        'steps': [
                            {'range': [0, 30], 'color': '#064e3b'},
                            {'range': [30, 50], 'color': '#1e3a5f'},
                            {'range': [50, 75], 'color': '#451a03'},
                            {'range': [75, 100], 'color': '#450a0a'}
                        ],
                        'threshold': {
                            'line': {'color': 'white', 'width': 2},
                            'thickness': 0.75, 'value': 50
                        }
                    }
                ))
                fig.update_layout(
                    height=220,
                    paper_bgcolor='rgba(0,0,0,0)',
                    plot_bgcolor='rgba(0,0,0,0)',
                    margin=dict(t=40, b=0, l=20, r=20)
                )
                st.plotly_chart(fig, use_container_width=True)

            with ch2:
                categories = ['Amount', 'C1 Address', 'C2 Usage', 'C4 Phone', 'C5 Email']
                values = [
                    min(amount/3000, 1.0),
                    min(C1/10, 1.0),
                    min(C2/10, 1.0),
                    min(C4/5, 1.0),
                    min(C5/5, 1.0)
                ]
                radar_color_fill = 'rgba(239,68,68,0.2)' if prediction=='FRAUD' else 'rgba(16,185,129,0.2)'
                radar_color_line = '#ef4444' if prediction=='FRAUD' else '#10b981'

                fig_radar = go.Figure(go.Scatterpolar(
                    r=values + [values[0]],
                    theta=categories + [categories[0]],
                    fill='toself',
                    fillcolor=radar_color_fill,
                    line_color=radar_color_line,
                    line_width=2
                ))
                fig_radar.update_layout(
                    polar=dict(
                        bgcolor='#0d1b2e',
                        radialaxis=dict(visible=True, range=[0,1],
                                      color='#475569', gridcolor='#1e3a5f'),
                        angularaxis=dict(color='#94a3b8', gridcolor='#1e3a5f')
                    ),
                    paper_bgcolor='rgba(0,0,0,0)',
                    height=220,
                    margin=dict(t=40, b=0, l=40, r=40),
                    title=dict(text='Risk Radar', font=dict(color='white', size=16))
                )
                st.plotly_chart(fig_radar, use_container_width=True)

            risk_data = {
                'Factor': ['Transaction Amount', 'Address Links (C1)',
                          'Usage Pattern (C2)', 'Phone Numbers (C4)', 'Email Accounts (C5)'],
                'Risk': [min(amount/3000,1.0), min(C1/10,1.0),
                        min(C2/10,1.0), min(C4/5,1.0), min(C5/5,1.0)]
            }
            df_risk = pd.DataFrame(risk_data).sort_values('Risk', ascending=True)

            fig_bar = go.Figure(go.Bar(
                x=df_risk['Risk'],
                y=df_risk['Factor'],
                orientation='h',
                marker_color=['#ef4444' if x > 0.5 else '#10b981' for x in df_risk['Risk']],
                text=[f"{x*100:.0f}%" for x in df_risk['Risk']],
                textposition='outside',
                textfont=dict(color='white')
            ))
            fig_bar.update_layout(
                title=dict(text='Risk Factor Breakdown', font=dict(color='white', size=16)),
                height=220,
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)',
                xaxis=dict(range=[0,1.2], color='#475569',
                          gridcolor='#1e3a5f', tickformat='.0%'),
                yaxis=dict(color='#94a3b8'),
                margin=dict(t=40, b=0, l=10, r=60)
            )
            st.plotly_chart(fig_bar, use_container_width=True)

            st.divider()
            report_data = {
                'prediction_id': result.get('prediction_id', 'N/A'),
                'prediction': prediction,
                'fraud_probability': fraud_prob,
                'alert_level': alert,
                'TransactionAmt': amount,
                'C1': C1, 'C2': C2, 'C4': C4, 'C5': C5
            }
            pdf_bytes = generate_fraud_report(report_data)
            st.download_button(
                label="Download Compliance Report (PDF)",
                data=pdf_bytes,
                file_name=f"fraudshield_report_{result.get('prediction_id', 'report')}.pdf",
                mime="application/pdf",
                use_container_width=True
            )

            st.divider()
            if prediction == "FRAUD":
                st.markdown(f"""
                <div style="background:#450a0a; border:1px solid #ef4444;
                     border-radius:10px; padding:16px;">
                    <p style="color:#f87171; font-weight:700; margin:0 0 8px 0; font-size:14px;">
                    Why this transaction was flagged:</p>
                    <p style="color:#fca5a5; margin:0; font-size:13px; line-height:1.8;">
                    Fraud probability: <strong>{fraud_prob*100:.1f}%</strong> (above 50% threshold)<br>
                    C1={C1} address links — {'suspicious' if C1>3 else 'normal'}<br>
                    C2={C2} usage pattern — {'suspicious' if C2>4 else 'normal'}<br>
                    C4={C4} phone numbers — {'suspicious' if C4>1 else 'normal'}<br>
                    Amount ${amount:,.2f} analyzed against 590K historical transactions
                    </p>
                </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown(f"""
                <div style="background:#064e3b; border:1px solid #10b981;
                     border-radius:10px; padding:16px;">
                    <p style="color:#34d399; font-weight:700; margin:0 0 8px 0; font-size:14px;">
                    Why this transaction is legitimate:</p>
                    <p style="color:#6ee7b7; margin:0; font-size:13px; line-height:1.8;">
                    Fraud probability: <strong>{fraud_prob*100:.1f}%</strong> (below 50% threshold)<br>
                    C1={C1} address links — normal range<br>
                    C2={C2} usage pattern — normal range<br>
                    C4={C4} phone numbers — normal range<br>
                    Transaction pattern consistent with legitimate behavior
                    </p>
                </div>
                """, unsafe_allow_html=True)

        except Exception as e:
            st.error(f"API Error: {e}")

    else:
        st.markdown("""
        <div style="background:#0d1b2e; border:1px solid #1e3a5f; border-radius:16px;
             padding:32px; text-align:center; margin-top:20px;">
            <h2 style="color:white; font-size:24px;">Enter transaction details to begin analysis</h2>
            <p style="color:#64748b; font-size:14px; margin-top:8px;">
            Powered by Graph Neural Networks + Random Forest</p>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)

        h1, h2, h3, h4 = st.columns(4)
        steps = [
            ("1", "Input", "Enter transaction amount and card behavior metrics"),
            ("2", "GNN", "GraphSAGE analyzes 13,553 node transaction graph"),
            ("3", "ML Model", "Random Forest predicts fraud probability"),
            ("4", "Decision", "Instant verdict with full risk breakdown")
        ]
        for col, (num, title, desc) in zip([h1, h2, h3, h4], steps):
            with col:
                st.markdown(f"""
                <div style="background:#0d1b2e; border:1px solid #1e3a5f;
                     border-radius:10px; padding:16px; text-align:center; height:140px;">
                    <p style="color:#185FA5; font-size:20px; font-weight:700; margin:0;">{num}</p>
                    <p style="color:white; font-weight:600; margin:8px 0 4px 0;">{title}</p>
                    <p style="color:#64748b; font-size:12px; margin:0;">{desc}</p>
                </div>
                """, unsafe_allow_html=True)

if st.session_state.history:
    st.divider()
    st.markdown('<div class="section-header">Transaction History — This Session</div>',
               unsafe_allow_html=True)

    history_df = pd.DataFrame(st.session_state.history)
    history_df['Risk %'] = (history_df['fraud_prob']*100).round(1).astype(str) + '%'
    history_df['Status'] = history_df['prediction'].apply(
        lambda x: 'FRAUD' if x=='FRAUD' else 'LEGIT'
    )
    history_df['Amount'] = history_df['amount'].apply(lambda x: f"${x:,.2f}")

    display_df = history_df[['time','Amount','C1','C2','C4','Risk %','Status']].rename(
        columns={'time': 'Time'}
    )
    st.dataframe(display_df, use_container_width=True, hide_index=True)

    if len(st.session_state.history) > 1:
        fig_trend = go.Figure()
        fig_trend.add_trace(go.Scatter(
            x=list(range(1, len(st.session_state.history)+1)),
            y=[h['fraud_prob']*100 for h in st.session_state.history],
            mode='lines+markers',
            line=dict(color='#3b82f6', width=2),
            marker=dict(
                color=['#ef4444' if h['prediction']=='FRAUD' else '#10b981'
                      for h in st.session_state.history],
                size=10
            ),
            name='Fraud Risk %'
        ))
        fig_trend.add_hline(y=50, line_dash="dash", line_color="#475569",
                           annotation_text="50% threshold",
                           annotation_font_color="#94a3b8")
        fig_trend.update_layout(
            title=dict(text='Fraud Risk Trend — This Session', font=dict(color='white')),
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            xaxis=dict(color='#475569', gridcolor='#1e3a5f', title='Transaction #'),
            yaxis=dict(color='#475569', gridcolor='#1e3a5f',
                      title='Fraud Risk %', range=[0,100]),
            height=250,
            showlegend=False
        )
        st.plotly_chart(fig_trend, use_container_width=True)

    if st.button("Clear History"):
        st.session_state.history = []
        st.rerun()