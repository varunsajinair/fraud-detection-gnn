import streamlit as st
import snowflake.connector
import os
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import numpy as np

st.set_page_config(
    page_title="FraudShield — Model Monitoring",
    page_icon="📡",
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
    <h1 style="margin:0;color:white;">📡 Model Monitoring Dashboard</h1>
    <p style="color:#64748b;margin:4px 0 0 0;">
    Track model performance, detect data drift, and monitor prediction health in production
    </p>
</div>
""", unsafe_allow_html=True)

@st.cache_data(ttl=60)
def load_all_predictions():
    try:
        conn = snowflake.connector.connect(
            user=st.secrets.get("SNOWFLAKE_USER") or os.getenv('SNOWFLAKE_USER'),
            password=st.secrets.get("SNOWFLAKE_PASSWORD") or os.getenv('SNOWFLAKE_PASSWORD'),
            account=st.secrets.get("SNOWFLAKE_ACCOUNT") or os.getenv('SNOWFLAKE_ACCOUNT', 'sxkobdu-fw40635'),
            warehouse='COMPUTE_WH',
            database='FRAUDSHIELD',
            schema='FRAUD_DETECTION'
        )
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM FRAUD_PREDICTIONS ORDER BY TIMESTAMP ASC")
        rows = cursor.fetchall()
        cols = [desc[0] for desc in cursor.description]
        df = pd.DataFrame(rows, columns=cols)
        cursor.close()
        conn.close()
        return df
    except Exception as e:
        st.error(f"Snowflake error: {e}")
        return pd.DataFrame()

df = load_all_predictions()

if df.empty:
    st.warning("No predictions found yet!")
    st.stop()

df['TIMESTAMP'] = pd.to_datetime(df['TIMESTAMP'])
df['DATE'] = df['TIMESTAMP'].dt.date
df['HOUR'] = df['TIMESTAMP'].dt.hour
df['IS_FRAUD'] = (df['PREDICTION'] == 'FRAUD').astype(int)

total = len(df)
fraud_count = df['IS_FRAUD'].sum()
fraud_rate = fraud_count / total * 100
avg_prob = df['FRAUD_PROBABILITY'].mean() * 100
high_risk = len(df[df['FRAUD_PROBABILITY'] > 0.8])

m1, m2, m3, m4, m5 = st.columns(5)
with m1: st.metric("Total Predictions", f"{total:,}")
with m2: st.metric("Fraud Detected", f"{int(fraud_count):,}")
with m3: st.metric("Fraud Rate", f"{fraud_rate:.1f}%")
with m4: st.metric("Avg Fraud Probability", f"{avg_prob:.1f}%")
with m5: st.metric("High Risk Transactions", f"{high_risk:,}")

st.divider()

# FRAUD RATE OVER TIME
st.markdown("### 📈 Fraud Rate Over Time")

daily = df.groupby('DATE').agg(
    total=('PREDICTION_ID', 'count'),
    fraud=('IS_FRAUD', 'sum'),
    avg_prob=('FRAUD_PROBABILITY', 'mean')
).reset_index()
daily['fraud_rate'] = daily['fraud'] / daily['total'] * 100

fig1 = go.Figure()
fig1.add_trace(go.Scatter(
    x=daily['DATE'], y=daily['fraud_rate'],
    mode='lines+markers',
    name='Fraud Rate %',
    line=dict(color='#dc2626', width=2),
    marker=dict(size=8),
    fill='tozeroy',
    fillcolor='rgba(220,38,38,0.1)'
))
fig1.add_hline(
    y=fraud_rate,
    line_dash="dash",
    line_color="#f97316",
    annotation_text=f"Overall avg: {fraud_rate:.1f}%",
    annotation_position="top right"
)
fig1.update_layout(
    paper_bgcolor='#0f172a', plot_bgcolor='#0f172a',
    font=dict(color='white'),
    xaxis=dict(gridcolor='#1e3a5f', color='white'),
    yaxis=dict(gridcolor='#1e3a5f', color='white', title='Fraud Rate (%)'),
    height=300, margin=dict(t=20, b=20)
)
st.plotly_chart(fig1, use_container_width=True)

st.divider()

# DATA DRIFT DETECTION
st.markdown("### 🔍 Data Drift Detection")
st.markdown("<p style='color:#64748b;font-size:13px;'>Compares recent predictions vs baseline — detects if input distribution is shifting (PSI score)</p>", unsafe_allow_html=True)

def compute_psi(expected, actual, bins=10):
    breakpoints = np.linspace(
        min(expected.min(), actual.min()),
        max(expected.max(), actual.max()), bins + 1
    )
    exp_counts = np.histogram(expected, bins=breakpoints)[0] + 1e-6
    act_counts = np.histogram(actual, bins=breakpoints)[0] + 1e-6
    exp_pct = exp_counts / exp_counts.sum()
    act_pct = act_counts / act_counts.sum()
    psi = np.sum((act_pct - exp_pct) * np.log(act_pct / exp_pct))
    return psi

col1, col2 = st.columns(2)

with col1:
    if len(df) >= 10:
        mid = len(df) // 2
        baseline_amt = df.iloc[:mid]['TRANSACTION_AMOUNT']
        recent_amt = df.iloc[mid:]['TRANSACTION_AMOUNT']

        fig2 = go.Figure()
        fig2.add_trace(go.Histogram(
            x=baseline_amt, name='Baseline (older)',
            marker_color='#185FA5', opacity=0.7, nbinsx=20
        ))
        fig2.add_trace(go.Histogram(
            x=recent_amt, name='Recent',
            marker_color='#dc2626', opacity=0.7, nbinsx=20
        ))
        fig2.update_layout(
            title='Transaction Amount Distribution Drift',
            barmode='overlay',
            paper_bgcolor='#0f172a', plot_bgcolor='#0f172a',
            font=dict(color='white'),
            xaxis=dict(gridcolor='#1e3a5f', color='white'),
            yaxis=dict(gridcolor='#1e3a5f', color='white'),
            height=300, margin=dict(t=40, b=20),
            legend=dict(bgcolor='#0f172a')
        )
        st.plotly_chart(fig2, use_container_width=True)

        psi = compute_psi(baseline_amt, recent_amt)
        if psi < 0.1:
            psi_status = "✅ No Drift"
            psi_color = "#059669"
            psi_msg = "Distribution is stable — model is healthy"
        elif psi < 0.2:
            psi_status = "⚠️ Minor Drift"
            psi_color = "#f97316"
            psi_msg = "Slight distribution shift — monitor closely"
        else:
            psi_status = "🚨 Major Drift!"
            psi_color = "#dc2626"
            psi_msg = "Significant drift detected — consider retraining!"

        st.markdown(f"""
        <div style="background:#0f172a;border:1px solid {psi_color};border-radius:8px;padding:16px;margin-top:8px;">
            <div style="display:flex;justify-content:space-between;align-items:center;">
                <span style="color:{psi_color};font-weight:bold;font-size:16px;">{psi_status}</span>
                <span style="color:white;font-weight:bold;">PSI Score: {psi:.4f}</span>
            </div>
            <p style="color:#64748b;margin:4px 0 0 0;font-size:12px;">{psi_msg}</p>
        </div>
        """, unsafe_allow_html=True)

with col2:
    if len(df) >= 10:
        baseline_prob = df.iloc[:mid]['FRAUD_PROBABILITY']
        recent_prob = df.iloc[mid:]['FRAUD_PROBABILITY']

        fig3 = go.Figure()
        fig3.add_trace(go.Histogram(
            x=baseline_prob, name='Baseline (older)',
            marker_color='#185FA5', opacity=0.7, nbinsx=20
        ))
        fig3.add_trace(go.Histogram(
            x=recent_prob, name='Recent',
            marker_color='#dc2626', opacity=0.7, nbinsx=20
        ))
        fig3.update_layout(
            title='Fraud Probability Score Distribution Drift',
            barmode='overlay',
            paper_bgcolor='#0f172a', plot_bgcolor='#0f172a',
            font=dict(color='white'),
            xaxis=dict(gridcolor='#1e3a5f', color='white'),
            yaxis=dict(gridcolor='#1e3a5f', color='white'),
            height=300, margin=dict(t=40, b=20),
            legend=dict(bgcolor='#0f172a')
        )
        st.plotly_chart(fig3, use_container_width=True)

        psi2 = compute_psi(baseline_prob, recent_prob)
        if psi2 < 0.1:
            psi2_status = "✅ No Drift"
            psi2_color = "#059669"
            psi2_msg = "Model confidence is stable"
        elif psi2 < 0.2:
            psi2_status = "⚠️ Minor Drift"
            psi2_color = "#f97316"
            psi2_msg = "Model confidence shifting slightly"
        else:
            psi2_status = "🚨 Major Drift!"
            psi2_color = "#dc2626"
            psi2_msg = "Model confidence drifting — check for concept drift!"

        st.markdown(f"""
        <div style="background:#0f172a;border:1px solid {psi2_color};border-radius:8px;padding:16px;margin-top:8px;">
            <div style="display:flex;justify-content:space-between;align-items:center;">
                <span style="color:{psi2_color};font-weight:bold;font-size:16px;">{psi2_status}</span>
                <span style="color:white;font-weight:bold;">PSI Score: {psi2:.4f}</span>
            </div>
            <p style="color:#64748b;margin:4px 0 0 0;font-size:12px;">{psi2_msg}</p>
        </div>
        """, unsafe_allow_html=True)

st.divider()

# PREDICTION CONFIDENCE OVER TIME
st.markdown("### 🎯 Model Confidence Over Time")

fig4 = go.Figure()
fraud_df = df[df['IS_FRAUD'] == 1]
legit_df = df[df['IS_FRAUD'] == 0]

fig4.add_trace(go.Scatter(
    x=fraud_df['TIMESTAMP'], y=fraud_df['FRAUD_PROBABILITY'],
    mode='markers', name='Fraud',
    marker=dict(color='#dc2626', size=8, opacity=0.7)
))
fig4.add_trace(go.Scatter(
    x=legit_df['TIMESTAMP'], y=legit_df['FRAUD_PROBABILITY'],
    mode='markers', name='Legitimate',
    marker=dict(color='#059669', size=6, opacity=0.5)
))
fig4.add_hline(y=0.5, line_dash="dash", line_color="#f97316",
               annotation_text="Decision threshold (0.5)")
fig4.update_layout(
    paper_bgcolor='#0f172a', plot_bgcolor='#0f172a',
    font=dict(color='white'),
    xaxis=dict(gridcolor='#1e3a5f', color='white'),
    yaxis=dict(gridcolor='#1e3a5f', color='white', title='Fraud Probability'),
    height=350, margin=dict(t=20, b=20),
    legend=dict(bgcolor='#0f172a')
)
st.plotly_chart(fig4, use_container_width=True)

st.divider()

# ALERT LEVEL BREAKDOWN + HOURLY HEATMAP
col3, col4 = st.columns(2)

with col3:
    st.markdown("### 🚨 Alert Level Distribution")
    alert_counts = df['ALERT_LEVEL'].value_counts().reset_index()
    alert_counts.columns = ['Alert Level', 'Count']

    color_map = {
        'CRITICAL': '#dc2626',
        'HIGH RISK': '#f97316',
        'MEDIUM RISK': '#fbbf24',
        'LOW RISK': '#059669',
        'LOW': '#059669'
    }
    colors = [color_map.get(a, '#185FA5') for a in alert_counts['Alert Level']]

    fig5 = go.Figure(go.Bar(
        x=alert_counts['Alert Level'],
        y=alert_counts['Count'],
        marker_color=colors
    ))
    fig5.update_layout(
        paper_bgcolor='#0f172a', plot_bgcolor='#0f172a',
        font=dict(color='white'),
        xaxis=dict(gridcolor='#1e3a5f', color='white'),
        yaxis=dict(gridcolor='#1e3a5f', color='white'),
        height=300, margin=dict(t=20, b=20)
    )
    st.plotly_chart(fig5, use_container_width=True)

with col4:
    st.markdown("### ⏰ Fraud by Hour of Day")
    hourly = df.groupby('HOUR').agg(
        total=('PREDICTION_ID', 'count'),
        fraud=('IS_FRAUD', 'sum')
    ).reset_index()
    hourly['fraud_rate'] = hourly['fraud'] / hourly['total'] * 100

    fig6 = go.Figure(go.Bar(
        x=hourly['HOUR'],
        y=hourly['fraud_rate'],
        marker_color='#185FA5',
        marker=dict(
            color=hourly['fraud_rate'],
            colorscale=[[0, '#059669'], [0.5, '#f97316'], [1, '#dc2626']],
            showscale=False
        )
    ))
    fig6.update_layout(
        paper_bgcolor='#0f172a', plot_bgcolor='#0f172a',
        font=dict(color='white'),
        xaxis=dict(gridcolor='#1e3a5f', color='white', title='Hour of Day'),
        yaxis=dict(gridcolor='#1e3a5f', color='white', title='Fraud Rate (%)'),
        height=300, margin=dict(t=20, b=20)
    )
    st.plotly_chart(fig6, use_container_width=True)

st.divider()

# MODEL HEALTH STATUS
st.markdown("### 🏥 Model Health Status")

health_checks = []

# Check 1: Fraud rate
if fraud_rate < 5:
    health_checks.append(("Fraud Rate", "✅ Normal", f"{fraud_rate:.1f}% — within expected range", "#059669"))
elif fraud_rate < 20:
    health_checks.append(("Fraud Rate", "⚠️ Elevated", f"{fraud_rate:.1f}% — above typical baseline", "#f97316"))
else:
    health_checks.append(("Fraud Rate", "🚨 Critical", f"{fraud_rate:.1f}% — extremely high!", "#dc2626"))

# Check 2: Avg confidence
if avg_prob < 60:
    health_checks.append(("Model Confidence", "✅ Good", f"Avg fraud prob: {avg_prob:.1f}%", "#059669"))
else:
    health_checks.append(("Model Confidence", "⚠️ High", f"Avg fraud prob: {avg_prob:.1f}% — many borderline cases", "#f97316"))

# Check 3: High risk volume
high_risk_rate = high_risk / total * 100
if high_risk_rate < 5:
    health_checks.append(("High Risk Volume", "✅ Normal", f"{high_risk} transactions ({high_risk_rate:.1f}%)", "#059669"))
else:
    health_checks.append(("High Risk Volume", "⚠️ Elevated", f"{high_risk} transactions ({high_risk_rate:.1f}%) — investigate!", "#f97316"))

# Check 4: Data drift
if psi < 0.1:
    health_checks.append(("Data Drift", "✅ Stable", "No significant distribution shift detected", "#059669"))
elif psi < 0.2:
    health_checks.append(("Data Drift", "⚠️ Minor Drift", "Monitor input distribution closely", "#f97316"))
else:
    health_checks.append(("Data Drift", "🚨 Major Drift", "Retraining recommended!", "#dc2626"))

cols = st.columns(4)
for i, (check_name, status, detail, color) in enumerate(health_checks):
    with cols[i]:
        st.markdown(f"""
        <div style="background:#0f172a;border:1px solid {color};border-radius:12px;
                    padding:16px;text-align:center;">
            <p style="color:#64748b;margin:0;font-size:11px;text-transform:uppercase;">{check_name}</p>
            <p style="color:{color};font-weight:bold;font-size:14px;margin:8px 0 4px 0;">{status}</p>
            <p style="color:#64748b;margin:0;font-size:11px;">{detail}</p>
        </div>
        """, unsafe_allow_html=True)

st.divider()

st.markdown("""
<div style="background:#0f172a;border:1px solid #1e3a5f;border-radius:8px;padding:16px;">
    <p style="color:#64748b;margin:0;font-size:13px;">
    💡 <b style="color:#cbd5e1;">PSI (Population Stability Index)</b> measures data drift:
    PSI &lt; 0.1 = stable, 0.1–0.2 = minor drift, &gt; 0.2 = major drift requiring model retraining.
    Banks use PSI as the industry standard metric for detecting when fraud models need retraining.
    </p>
</div>
""", unsafe_allow_html=True)