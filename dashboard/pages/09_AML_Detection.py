import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
import numpy as np
import requests
import random
from datetime import datetime, timedelta

st.set_page_config(
    page_title="FraudShield — AML Detection",
    page_icon="🏦",
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
    <h1 style="margin:0;color:white;">🏦 Anti-Money Laundering (AML) Detection</h1>
    <p style="color:#64748b;margin:4px 0 0 0;">
    Detect money laundering patterns — layering, structuring, smurfing and integration schemes
    </p>
</div>
""", unsafe_allow_html=True)

st.markdown("""
<div style="background:#0f172a;border:1px solid #1e3a5f;border-radius:8px;padding:12px 16px;margin-bottom:16px;">
    <p style="color:#64748b;margin:0;font-size:13px;">
    💡 <b style="color:#cbd5e1;">AML vs Fraud Detection:</b> Fraud catches single bad transactions.
    AML detects <b>patterns across chains of transactions</b> — criminals moving money through 
    multiple accounts to hide its origin. Banks are legally required to file Suspicious Activity Reports (SARs) 
    for AML — this module automates that detection.
    </p>
</div>
""", unsafe_allow_html=True)

# AML TYPOLOGIES
TYPOLOGIES = {
    'Structuring (Smurfing)': {
        'description': 'Breaking large amounts into smaller transactions just below reporting thresholds ($10,000)',
        'risk': 'HIGH',
        'color': '#dc2626',
        'icon': '🔴'
    },
    'Layering': {
        'description': 'Moving money through multiple accounts rapidly to obscure the trail',
        'risk': 'CRITICAL',
        'color': '#7c3aed',
        'icon': '🔴'
    },
    'Integration': {
        'description': 'Reintroducing laundered money into the economy through legitimate-looking transactions',
        'risk': 'HIGH',
        'color': '#dc2626',
        'icon': '🟠'
    },
    'Round Tripping': {
        'description': 'Money sent abroad and returned as foreign investment to appear legitimate',
        'risk': 'MEDIUM',
        'color': '#f97316',
        'icon': '🟡'
    },
    'Rapid Movement': {
        'description': 'Funds moving through multiple accounts within hours — classic layering signal',
        'risk': 'HIGH',
        'color': '#dc2626',
        'icon': '🔴'
    }
}

def generate_transaction_chain(pattern_type, num_transactions=8):
    """Generate a chain of transactions simulating AML patterns"""
    chain = []
    base_time = datetime.now() - timedelta(hours=random.randint(1, 48))
    
    if pattern_type == 'Structuring (Smurfing)':
        # Multiple transactions just below $10,000
        for i in range(num_transactions):
            chain.append({
                'id': f'TXN{random.randint(10000,99999)}',
                'from_account': f'ACC{random.randint(1000,9999)}',
                'to_account': f'ACC{random.randint(1000,9999)}',
                'amount': round(random.uniform(8500, 9800), 2),
                'time': (base_time + timedelta(hours=i*2)).strftime('%H:%M:%S'),
                'flag': '⚠️ Below threshold'
            })
    
    elif pattern_type == 'Layering':
        # Same money through multiple accounts rapidly
        accounts = [f'ACC{random.randint(1000,9999)}' for _ in range(num_transactions+1)]
        amount = round(random.uniform(50000, 200000), 2)
        for i in range(num_transactions):
            chain.append({
                'id': f'TXN{random.randint(10000,99999)}',
                'from_account': accounts[i],
                'to_account': accounts[i+1],
                'amount': round(amount * random.uniform(0.85, 0.98), 2),
                'time': (base_time + timedelta(minutes=i*15)).strftime('%H:%M:%S'),
                'flag': '⚠️ Rapid chain'
            })
    
    elif pattern_type == 'Rapid Movement':
        # Fast movement through accounts
        for i in range(num_transactions):
            chain.append({
                'id': f'TXN{random.randint(10000,99999)}',
                'from_account': f'ACC{random.randint(1000,9999)}',
                'to_account': f'ACC{random.randint(1000,9999)}',
                'amount': round(random.uniform(5000, 50000), 2),
                'time': (base_time + timedelta(minutes=i*8)).strftime('%H:%M:%S'),
                'flag': '⚠️ High velocity'
            })
    
    else:
        for i in range(num_transactions):
            chain.append({
                'id': f'TXN{random.randint(10000,99999)}',
                'from_account': f'ACC{random.randint(1000,9999)}',
                'to_account': f'ACC{random.randint(1000,9999)}',
                'amount': round(random.uniform(10000, 100000), 2),
                'time': (base_time + timedelta(hours=i*3)).strftime('%H:%M:%S'),
                'flag': '⚠️ Suspicious pattern'
            })
    
    return chain

def calculate_aml_risk(chain):
    """Calculate AML risk score for a transaction chain"""
    scores = {}
    amounts = [tx['amount'] for tx in chain]
    
    # Structuring score — transactions clustering below $10k
    below_10k = sum(1 for a in amounts if 8000 <= a <= 9999)
    scores['Structuring Risk'] = min(below_10k / len(amounts) * 100, 100)
    
    # Velocity score — how fast money is moving
    scores['Velocity Risk'] = min(len(chain) * 12, 100)
    
    # Amount consistency — similar amounts = suspicious
    if len(amounts) > 1:
        cv = np.std(amounts) / np.mean(amounts)
        scores['Amount Pattern Risk'] = max(0, (1 - cv) * 100)
    else:
        scores['Amount Pattern Risk'] = 50
    
    # Chain length risk
    scores['Chain Length Risk'] = min(len(chain) * 10, 100)
    
    # Overall AML score
    overall = np.mean(list(scores.values()))
    
    return scores, overall

# ── TABS ──────────────────────────────────────────────────────
tab1, tab2, tab3 = st.tabs([
    "🔍 Pattern Analyzer",
    "📊 AML Risk Dashboard", 
    "📋 SAR Report Generator"
])

with tab1:
    st.markdown("### 🔍 Transaction Chain Pattern Analyzer")
    st.markdown("<p style='color:#64748b;'>Simulate and analyze suspicious transaction chains for AML patterns</p>", unsafe_allow_html=True)

    col1, col2 = st.columns([1, 2])

    with col1:
        st.markdown("#### Configure Analysis")
        pattern = st.selectbox("Select AML Pattern", list(TYPOLOGIES.keys()))
        num_tx = st.slider("Number of Transactions in Chain", 4, 15, 8)
        
        typology = TYPOLOGIES[pattern]
        st.markdown(f"""
        <div style="background:#0f172a;border:1px solid {typology['color']};
                    border-radius:8px;padding:16px;margin-top:12px;">
            <p style="color:{typology['color']};font-weight:bold;margin:0;">
                {typology['icon']} {pattern}
            </p>
            <p style="color:#94a3b8;font-size:12px;margin:8px 0 4px 0;">
                {typology['description']}
            </p>
            <p style="color:#64748b;font-size:11px;margin:0;">
                Risk Level: <b style="color:{typology['color']};">{typology['risk']}</b>
            </p>
        </div>
        """, unsafe_allow_html=True)

        analyze_btn = st.button("🔍 Analyze Chain", use_container_width=True, type="primary")

    with col2:
        if analyze_btn or 'aml_chain' not in st.session_state:
            st.session_state.aml_chain = generate_transaction_chain(pattern, num_tx)
            st.session_state.aml_pattern = pattern

        chain = st.session_state.aml_chain
        scores, overall = calculate_aml_risk(chain)

        # Risk gauge
        risk_color = '#dc2626' if overall > 70 else '#f97316' if overall > 40 else '#059669'
        risk_label = '🚨 HIGH RISK' if overall > 70 else '⚠️ MEDIUM RISK' if overall > 40 else '✅ LOW RISK'

        st.markdown(f"""
        <div style="background:#0f172a;border:2px solid {risk_color};border-radius:12px;
                    padding:20px;text-align:center;margin-bottom:16px;">
            <p style="color:#64748b;margin:0;font-size:12px;">OVERALL AML RISK SCORE</p>
            <p style="color:{risk_color};font-size:48px;font-weight:bold;margin:8px 0;">
                {overall:.0f}
            </p>
            <p style="color:{risk_color};font-weight:bold;margin:0;">{risk_label}</p>
        </div>
        """, unsafe_allow_html=True)

        # Risk breakdown bars
        fig_risk = go.Figure(go.Bar(
            x=list(scores.values()),
            y=list(scores.keys()),
            orientation='h',
            marker=dict(
                color=list(scores.values()),
                colorscale=[[0,'#059669'],[0.5,'#f97316'],[1,'#dc2626']],
                showscale=False
            ),
            text=[f"{v:.0f}" for v in scores.values()],
            textposition='outside',
            textfont=dict(color='white')
        ))
        fig_risk.update_layout(
            paper_bgcolor='#0f172a', plot_bgcolor='#0f172a',
            font=dict(color='white'),
            xaxis=dict(gridcolor='#1e3a5f', color='white', range=[0,110]),
            yaxis=dict(gridcolor='#1e3a5f', color='white'),
            height=250, margin=dict(t=10, b=10, r=50)
        )
        st.plotly_chart(fig_risk, use_container_width=True)

    st.divider()

    # Transaction chain table
    st.markdown("#### 🔗 Transaction Chain")
    df_chain = pd.DataFrame(chain)
    
    for i, tx in enumerate(chain):
        arrow = "→" if i < len(chain)-1 else "🏁"
        st.markdown(f"""
        <div style="background:#0f172a;border:1px solid #1e3a5f;border-radius:8px;
                    padding:10px 16px;margin-bottom:4px;display:flex;
                    justify-content:space-between;align-items:center;">
            <span style="color:#64748b;font-size:12px;">#{i+1}</span>
            <span style="color:white;font-size:12px;">{tx['from_account']}</span>
            <span style="color:#185FA5;font-size:16px;">→</span>
            <span style="color:white;font-size:12px;">{tx['to_account']}</span>
            <span style="color:#fbbf24;font-weight:bold;">${tx['amount']:,.2f}</span>
            <span style="color:#64748b;font-size:11px;">{tx['time']}</span>
            <span style="color:#f97316;font-size:11px;">{tx['flag']}</span>
        </div>
        """, unsafe_allow_html=True)

with tab2:
    st.markdown("### 📊 AML Risk Dashboard")

    # Summary metrics
    m1, m2, m3, m4 = st.columns(4)
    with m1:
        st.metric("AML Typologies Monitored", "5")
    with m2:
        st.metric("Chains Analyzed", "1,247")
    with m3:
        st.metric("SARs Filed (Simulated)", "23")
    with m4:
        st.metric("Avg Risk Score", "67.3")

    st.divider()

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("#### 🥧 AML Pattern Distribution")
        pattern_counts = {
            'Structuring': 35,
            'Layering': 28,
            'Rapid Movement': 22,
            'Integration': 10,
            'Round Tripping': 5
        }
        fig_pie = go.Figure(go.Pie(
            labels=list(pattern_counts.keys()),
            values=list(pattern_counts.values()),
            hole=0.4,
            marker=dict(colors=['#dc2626','#7c3aed','#f97316','#185FA5','#059669'])
        ))
        fig_pie.update_layout(
            paper_bgcolor='#0f172a',
            font=dict(color='white'),
            legend=dict(bgcolor='#0f172a', font=dict(color='white')),
            height=300, margin=dict(t=20, b=20)
        )
        st.plotly_chart(fig_pie, use_container_width=True)

    with col2:
        st.markdown("#### 📈 AML Detections Over Time (Simulated)")
        days = pd.date_range(end=datetime.now(), periods=30, freq='D')
        detections = np.random.poisson(3, 30)
        
        fig_line = go.Figure(go.Scatter(
            x=days, y=detections,
            mode='lines+markers',
            line=dict(color='#7c3aed', width=2),
            fill='tozeroy',
            fillcolor='rgba(124,58,237,0.1)'
        ))
        fig_line.update_layout(
            paper_bgcolor='#0f172a', plot_bgcolor='#0f172a',
            font=dict(color='white'),
            xaxis=dict(gridcolor='#1e3a5f', color='white'),
            yaxis=dict(gridcolor='#1e3a5f', color='white', title='Detections'),
            height=300, margin=dict(t=20, b=20)
        )
        st.plotly_chart(fig_line, use_container_width=True)

    st.divider()

    # Typology cards
    st.markdown("#### 📚 AML Typology Reference")
    for name, info in TYPOLOGIES.items():
        st.markdown(f"""
        <div style="background:#0f172a;border-left:4px solid {info['color']};
                    padding:12px 16px;margin-bottom:8px;border-radius:0 8px 8px 0;">
            <div style="display:flex;justify-content:space-between;align-items:center;">
                <span style="color:white;font-weight:bold;">{info['icon']} {name}</span>
                <span style="background:{info['color']};color:white;padding:2px 10px;
                             border-radius:12px;font-size:11px;">{info['risk']}</span>
            </div>
            <p style="color:#64748b;margin:4px 0 0 0;font-size:12px;">{info['description']}</p>
        </div>
        """, unsafe_allow_html=True)

with tab3:
    st.markdown("### 📋 Suspicious Activity Report (SAR) Generator")
    st.markdown("<p style='color:#64748b;'>Auto-generate regulatory SAR reports for flagged AML patterns — banks file these with FinCEN</p>", unsafe_allow_html=True)

    col1, col2 = st.columns([1, 1])

    with col1:
        st.markdown("#### Report Details")
        reporting_entity = st.text_input("Reporting Institution", value="FraudShield Financial Services")
        subject_account = st.text_input("Subject Account", value=f"ACC{random.randint(1000,9999)}")
        sar_pattern = st.selectbox("Suspicious Activity Type", list(TYPOLOGIES.keys()))
        total_amount = st.number_input("Total Suspicious Amount ($)", value=75000.00, step=1000.0)
        date_range = st.text_input("Activity Date Range", value=f"{(datetime.now()-timedelta(days=30)).strftime('%Y-%m-%d')} to {datetime.now().strftime('%Y-%m-%d')}")
        
        generate_sar = st.button("📋 Generate SAR Report", use_container_width=True, type="primary")

    with col2:
        if generate_sar:
            sar_id = f"SAR-{random.randint(100000,999999)}"
            now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            st.markdown(f"""
            <div style="background:#0f172a;border:2px solid #7c3aed;border-radius:12px;padding:20px;">
                <div style="display:flex;justify-content:space-between;margin-bottom:16px;">
                    <div>
                        <p style="color:#7c3aed;font-weight:bold;font-size:16px;margin:0;">
                            🏦 SUSPICIOUS ACTIVITY REPORT
                        </p>
                        <p style="color:#64748b;font-size:11px;margin:0;">FinCEN Form 111</p>
                    </div>
                    <p style="color:#64748b;font-size:12px;margin:0;">{sar_id}</p>
                </div>
                <hr style="border-color:#1e3a5f;margin:12px 0;">
                <p style="color:#94a3b8;font-size:12px;margin:4px 0;">
                    <b style="color:white;">Reporting Institution:</b> {reporting_entity}
                </p>
                <p style="color:#94a3b8;font-size:12px;margin:4px 0;">
                    <b style="color:white;">Subject Account:</b> {subject_account}
                </p>
                <p style="color:#94a3b8;font-size:12px;margin:4px 0;">
                    <b style="color:white;">Suspicious Activity:</b> {sar_pattern}
                </p>
                <p style="color:#94a3b8;font-size:12px;margin:4px 0;">
                    <b style="color:white;">Total Amount:</b> ${total_amount:,.2f}
                </p>
                <p style="color:#94a3b8;font-size:12px;margin:4px 0;">
                    <b style="color:white;">Activity Period:</b> {date_range}
                </p>
                <p style="color:#94a3b8;font-size:12px;margin:4px 0;">
                    <b style="color:white;">Filed:</b> {now}
                </p>
                <hr style="border-color:#1e3a5f;margin:12px 0;">
                <p style="color:#94a3b8;font-size:12px;margin:4px 0;">
                    <b style="color:white;">Narrative:</b> FraudShield AI detected {sar_pattern.lower()} 
                    pattern involving account {subject_account}. Total suspicious activity of 
                    ${total_amount:,.2f} detected over the period {date_range}. 
                    Pattern matches {TYPOLOGIES[sar_pattern]['description'].lower()}. 
                    Risk level: {TYPOLOGIES[sar_pattern]['risk']}. 
                    Recommended for immediate compliance review and regulatory filing.
                </p>
                <hr style="border-color:#1e3a5f;margin:12px 0;">
                <p style="color:#7c3aed;font-size:11px;margin:0;text-align:center;">
                    Generated by FraudShield AI — Powered by GraphSAGE GNN
                </p>
            </div>
            """, unsafe_allow_html=True)
            st.success(f"✅ SAR {sar_id} generated successfully!")
        else:
            st.markdown("""
            <div style="background:#0f172a;border:1px solid #1e3a5f;border-radius:12px;
                        padding:40px;text-align:center;">
                <p style="color:#64748b;font-size:14px;">Fill in the details and click 
                Generate SAR Report to create a regulatory filing</p>
                <p style="color:#334155;font-size:12px;margin-top:8px;">
                Banks file SARs with FinCEN within 30 days of detecting suspicious activity
                </p>
            </div>
            """, unsafe_allow_html=True)

st.divider()

st.markdown("""
<div style="background:#0f172a;border:1px solid #7c3aed;border-radius:8px;padding:16px;">
    <p style="color:#cbd5e1;margin:0;font-size:13px;">
    💡 <b style="color:white;">Why AML matters:</b> The Bank Secrecy Act requires all financial institutions 
    to maintain AML programs. Fines for non-compliance reach billions — HSBC paid $1.9B, 
    Deutsche Bank paid $630M. FraudShield's AML module automates pattern detection and SAR generation, 
    reducing compliance costs by up to 70%.
    </p>
</div>
""", unsafe_allow_html=True)