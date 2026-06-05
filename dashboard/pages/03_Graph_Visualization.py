import streamlit as st
import networkx as nx
from pyvis.network import Network
import pandas as pd
import snowflake.connector
import os
import tempfile
import streamlit.components.v1 as components

st.set_page_config(
    page_title="FraudShield — Graph Visualization",
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
    <h1 style="margin:0;color:white;font-size:28px;">Transaction Graph</h1>
    <p style="color:#64748b;margin:6px 0 0 0;font-size:13px;">
        Interactive graph of transaction connections — red nodes are fraud, green are legitimate
    </p>
</div>
""", unsafe_allow_html=True)

@st.cache_data(ttl=60)
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
        cursor.execute("SELECT * FROM FRAUD_PREDICTIONS ORDER BY TIMESTAMP DESC LIMIT 50")
        rows = cursor.fetchall()
        cols = [desc[0] for desc in cursor.description]
        df = pd.DataFrame(rows, columns=cols)
        cursor.close()
        conn.close()
        return df
    except Exception as e:
        st.error(f"Snowflake error: {e}")
        return pd.DataFrame()

df = load_data()

if df.empty:
    st.warning("No predictions found. Make some predictions first.")
    st.stop()

total = len(df)
fraud_count = len(df[df['PREDICTION'] == 'FRAUD'])
legit_count = len(df[df['PREDICTION'] == 'LEGITIMATE'])

m1, m2, m3, m4 = st.columns(4)
with m1: st.metric("Transactions in Graph", total)
with m2: st.metric("Fraud Nodes", fraud_count)
with m3: st.metric("Legitimate Nodes", legit_count)
with m4: st.metric("Graph Density", f"{(total/(total*total))*100:.1f}%")

st.divider()

col1, col2, col3 = st.columns(3)
with col1:
    show_fraud_only = st.checkbox("Show Fraud Nodes Only", value=False)
with col2:
    node_size = st.slider("Node Size", 10, 50, 25)
with col3:
    physics = st.checkbox("Enable Physics Animation", value=True)

st.divider()

net = Network(
    height="600px",
    width="100%",
    bgcolor="#0a0e1a",
    font_color="white",
    directed=False
)

if physics:
    net.barnes_hut(
        gravity=-5000,
        central_gravity=0.3,
        spring_length=200,
        spring_strength=0.05,
        damping=0.09
    )

if show_fraud_only:
    df_plot = df[df['PREDICTION'] == 'FRAUD']
else:
    df_plot = df

net.add_node(
    'FRAUDSHIELD_SYSTEM',
    label='FraudShield\nAI System',
    color='#185FA5',
    size=40,
    shape='diamond',
    font={'size': 12, 'color': 'white'},
    title='Central Fraud Detection System'
)

for _, row in df_plot.iterrows():
    pid = row['PREDICTION_ID']
    is_fraud = row['PREDICTION'] == 'FRAUD'
    prob = row['FRAUD_PROBABILITY']
    amount = row['TRANSACTION_AMOUNT']

    color = '#dc2626' if is_fraud else '#059669'
    size = node_size + int(prob * 20)
    shape = 'star' if is_fraud else 'dot'

    label = f"{pid[:6]}\n${amount:.0f}"
    title = f"""
    <div style='background:#1e293b;padding:10px;border-radius:8px;color:white;'>
        <b>Transaction ID:</b> {pid}<br>
        <b>Amount:</b> ${amount:,.2f}<br>
        <b>Prediction:</b> {row['PREDICTION']}<br>
        <b>Fraud Probability:</b> {prob*100:.1f}%<br>
        <b>Alert Level:</b> {row['ALERT_LEVEL']}<br>
        <b>C1:</b> {row['C1']} | <b>C2:</b> {row['C2']} | <b>C4:</b> {row['C4']}
    </div>
    """

    net.add_node(
        pid,
        label=label,
        color=color,
        size=size,
        shape=shape,
        font={'size': 9, 'color': 'white'},
        title=title,
        borderWidth=2,
        borderWidthSelected=4
    )

    edge_color = '#dc2626' if is_fraud else '#059669'
    edge_width = 3 if is_fraud else 1
    net.add_edge(
        'FRAUDSHIELD_SYSTEM',
        pid,
        color=edge_color,
        width=edge_width,
        dashes=not is_fraud
    )

fraud_nodes = df_plot[df_plot['PREDICTION'] == 'FRAUD']
fraud_list = fraud_nodes.to_dict('records')
for i in range(len(fraud_list)):
    for j in range(i+1, len(fraud_list)):
        n1 = fraud_list[i]
        n2 = fraud_list[j]
        if abs(n1['C1'] - n2['C1']) <= 1 or abs(n1['C2'] - n2['C2']) <= 1:
            net.add_edge(
                n1['PREDICTION_ID'],
                n2['PREDICTION_ID'],
                color='#f97316',
                width=1.5,
                dashes=True,
                title='Similar fraud pattern detected'
            )

with tempfile.NamedTemporaryFile(delete=False, suffix='.html', mode='w') as f:
    net.save_graph(f.name)
    html_content = open(f.name, 'r').read()

components.html(html_content, height=620)

st.divider()

st.markdown("""
<div style="display:flex;gap:20px;flex-wrap:wrap;">
    <div style="display:flex;align-items:center;gap:8px;">
        <div style="width:16px;height:16px;background:#dc2626;border-radius:50%;"></div>
        <span style="color:#cbd5e1;font-size:13px;">Fraud Transaction (star shape)</span>
    </div>
    <div style="display:flex;align-items:center;gap:8px;">
        <div style="width:16px;height:16px;background:#059669;border-radius:50%;"></div>
        <span style="color:#cbd5e1;font-size:13px;">Legitimate Transaction (circle)</span>
    </div>
    <div style="display:flex;align-items:center;gap:8px;">
        <div style="width:16px;height:16px;background:#185FA5;border-radius:4px;"></div>
        <span style="color:#cbd5e1;font-size:13px;">FraudShield System (hub)</span>
    </div>
    <div style="display:flex;align-items:center;gap:8px;">
        <div style="width:16px;height:3px;background:#f97316;"></div>
        <span style="color:#cbd5e1;font-size:13px;">Similar fraud pattern connection</span>
    </div>
</div>
""", unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)
st.caption("Click and drag nodes to explore. Hover over nodes for full transaction details. Larger nodes = higher fraud probability.")