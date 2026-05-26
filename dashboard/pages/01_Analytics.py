import streamlit as st
import plotly.graph_objects as go
import pandas as pd
import snowflake.connector
import os
from datetime import datetime

st.set_page_config(
    page_title="FraudShield — Analytics",
    page_icon="📊",
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

st.markdown("# 📊 FraudShield Analytics")
st.markdown("#### Live data from Snowflake — All predictions ever made")
st.divider()

@st.cache_data(ttl=30)
def load_data():
    try:
        conn = snowflake.connector.connect(
            user=os.getenv('SNOWFLAKE_USER'),
            password=os.getenv('SNOWFLAKE_PASSWORD'),
            account=os.getenv('SNOWFLAKE_ACCOUNT', 'sxkobdu-fw40635'),
            warehouse='COMPUTE_WH',
            database='FRAUDSHIELD',
            schema='FRAUD_DETECTION'
        )
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM FRAUD_PREDICTIONS ORDER BY TIMESTAMP DESC")
        rows = cursor.fetchall()
        cols = [desc[0] for desc in cursor.description]
        df = pd.DataFrame(rows, columns=cols)
        cursor.close()
        conn.close()
        return df
    except Exception as e:
        st.error(f"Snowflake connection error: {e}")
        return pd.DataFrame()

df = load_data()

if df.empty:
    st.warning("No predictions found in Snowflake yet. Make some predictions first!")
    st.stop()

df['TIMESTAMP'] = pd.to_datetime(df['TIMESTAMP'])

# ── TOP METRICS ───────────────────────────────────────────
total = len(df)
fraud_count = len(df[df['PREDICTION'] == 'FRAUD'])
legit_count = len(df[df['PREDICTION'] == 'LEGITIMATE'])
fraud_rate = (fraud_count / total * 100) if total > 0 else 0
avg_prob = df['FRAUD_PROBABILITY'].mean() * 100
total_amount = df['TRANSACTION_AMOUNT'].sum()
fraud_amount = df[df['PREDICTION'] == 'FRAUD']['TRANSACTION_AMOUNT'].sum()

m1, m2, m3, m4, m5, m6 = st.columns(6)
with m1: st.metric("Total Analyzed", f"{total:,}")
with m2: st.metric("Fraud Detected", f"{fraud_count:,}", delta=f"{fraud_rate:.1f}% rate")
with m3: st.metric("Legitimate", f"{legit_count:,}")
with m4: st.metric("Avg Risk Score", f"{avg_prob:.1f}%")
with m5: st.metric("Total Volume", f"${total_amount:,.0f}")
with m6: st.metric("Fraud Amount", f"${fraud_amount:,.0f}", delta_color="inverse")

st.divider()

# ── ROW 1 ─────────────────────────────────────────────────
r1c1, r1c2, r1c3 = st.columns(3)

with r1c1:
    fig = go.Figure(go.Pie(
        labels=['Legitimate', 'Fraud'],
        values=[legit_count, fraud_count],
        hole=0.6,
        marker_colors=['#059669', '#dc2626'],
    ))
    fig.update_layout(
        title=dict(text='Fraud vs Legitimate', font=dict(color='white')),
        paper_bgcolor='rgba(0,0,0,0)',
        font=dict(color='white'),
        height=280,
        legend=dict(font=dict(color='white'))
    )
    fig.add_annotation(text=f'{fraud_rate:.1f}%<br>Fraud', x=0.5, y=0.5,
                      font=dict(size=14, color='white'), showarrow=False)
    st.plotly_chart(fig, use_container_width=True)

with r1c2:
    alert_counts = df['ALERT_LEVEL'].value_counts()
    alert_colors = {'SAFE': '#059669', 'LOW RISK': '#185FA5',
                   'HIGH RISK': '#f97316', 'CRITICAL': '#dc2626'}
    fig2 = go.Figure(go.Bar(
        x=alert_counts.index,
        y=alert_counts.values,
        marker_color=[alert_colors.get(a, '#185FA5') for a in alert_counts.index],
        text=alert_counts.values,
        textposition='outside',
        textfont=dict(color='white')
    ))
    fig2.update_layout(
        title=dict(text='Alert Level Distribution', font=dict(color='white')),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        xaxis=dict(color='#475569', gridcolor='#1e3a5f'),
        yaxis=dict(color='#475569', gridcolor='#1e3a5f'),
        height=280,
        font=dict(color='white')
    )
    st.plotly_chart(fig2, use_container_width=True)

with r1c3:
    fig3 = go.Figure()
    fig3.add_trace(go.Box(
        y=df[df['PREDICTION']=='LEGITIMATE']['TRANSACTION_AMOUNT'],
        name='Legitimate', marker_color='#059669'
    ))
    fig3.add_trace(go.Box(
        y=df[df['PREDICTION']=='FRAUD']['TRANSACTION_AMOUNT'],
        name='Fraud', marker_color='#dc2626'
    ))
    fig3.update_layout(
        title=dict(text='Amount Distribution', font=dict(color='white')),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        yaxis=dict(color='#475569', gridcolor='#1e3a5f', title='Amount ($)'),
        height=280,
        font=dict(color='white'),
        legend=dict(font=dict(color='white'))
    )
    st.plotly_chart(fig3, use_container_width=True)

# ── ROW 2 ─────────────────────────────────────────────────
r2c1, r2c2 = st.columns(2)

with r2c1:
    fig4 = go.Figure()
    fig4.add_trace(go.Histogram(
        x=df[df['PREDICTION']=='LEGITIMATE']['FRAUD_PROBABILITY']*100,
        name='Legitimate', marker_color='#059669', opacity=0.7, nbinsx=20
    ))
    fig4.add_trace(go.Histogram(
        x=df[df['PREDICTION']=='FRAUD']['FRAUD_PROBABILITY']*100,
        name='Fraud', marker_color='#dc2626', opacity=0.7, nbinsx=20
    ))
    fig4.add_vline(x=50, line_dash="dash", line_color="white",
                  annotation_text="50% threshold", annotation_font_color="white")
    fig4.update_layout(
        title=dict(text='Fraud Probability Distribution', font=dict(color='white')),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        xaxis=dict(color='#475569', gridcolor='#1e3a5f', title='Fraud Probability (%)'),
        yaxis=dict(color='#475569', gridcolor='#1e3a5f', title='Count'),
        height=280,
        barmode='overlay',
        font=dict(color='white'),
        legend=dict(font=dict(color='white'))
    )
    st.plotly_chart(fig4, use_container_width=True)

with r2c2:
    if len(df) > 1:
        df_sorted = df.sort_values('TIMESTAMP')
        fig5 = go.Figure()
        fig5.add_trace(go.Scatter(
            x=df_sorted['TIMESTAMP'],
            y=df_sorted['FRAUD_PROBABILITY']*100,
            mode='lines+markers',
            line=dict(color='#3b82f6', width=2),
            marker=dict(
                color=['#dc2626' if p=='FRAUD' else '#059669'
                      for p in df_sorted['PREDICTION']],
                size=8
            ),
        ))
        fig5.add_hline(y=50, line_dash="dash", line_color="#475569",
                      annotation_text="Threshold", annotation_font_color="#94a3b8")
        fig5.update_layout(
            title=dict(text='Fraud Risk Timeline', font=dict(color='white')),
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            xaxis=dict(color='#475569', gridcolor='#1e3a5f'),
            yaxis=dict(color='#475569', gridcolor='#1e3a5f',
                      title='Risk Score (%)', range=[0,100]),
            height=280,
            showlegend=False,
            font=dict(color='white')
        )
        st.plotly_chart(fig5, use_container_width=True)
    else:
        st.info("Make more predictions to see the timeline!")

st.divider()

# ── ALL PREDICTIONS TABLE ─────────────────────────────────
st.markdown("### 📋 All Predictions — Snowflake Database")

display = df[['PREDICTION_ID', 'TIMESTAMP', 'TRANSACTION_AMOUNT',
              'C1', 'C2', 'C4', 'FRAUD_PROBABILITY', 'PREDICTION', 'ALERT_LEVEL']].copy()
display['FRAUD_PROBABILITY'] = (display['FRAUD_PROBABILITY']*100).round(1).astype(str) + '%'
display['TRANSACTION_AMOUNT'] = display['TRANSACTION_AMOUNT'].apply(lambda x: f'${x:,.2f}')
display['TIMESTAMP'] = display['TIMESTAMP'].dt.strftime('%Y-%m-%d %H:%M:%S')

st.dataframe(display, use_container_width=True, hide_index=True)

csv = df.to_csv(index=False)
st.download_button(
    label="📥 Export All Data (CSV)",
    data=csv,
    file_name=f"fraudshield_analytics_{datetime.now().strftime('%Y%m%d')}.csv",
    mime="text/csv",
    use_container_width=True
)