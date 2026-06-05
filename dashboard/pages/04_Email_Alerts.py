import streamlit as st
import snowflake.connector
import os
import pandas as pd
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
from datetime import datetime

st.set_page_config(
    page_title="FraudShield — Email Alerts",
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
    <h1 style="margin:0;color:white;font-size:28px;">Email Alerts</h1>
    <p style="color:#64748b;margin:6px 0 0 0;font-size:13px;">
        Send fraud alert emails via SendGrid for flagged transactions
    </p>
</div>
""", unsafe_allow_html=True)

SENDGRID_API_KEY = st.secrets.get("SENDGRID_API_KEY") or os.getenv('SENDGRID_API_KEY')
FROM_EMAIL = "varunsajinair@gmail.com"

def send_fraud_alert(to_email, transaction_data):
    subject = f"FraudShield Alert: Suspicious Transaction — ${transaction_data['amount']:,.2f}"

    html_content = f"""
    <div style="font-family:Arial,sans-serif;background:#0a0e1a;padding:32px;border-radius:16px;max-width:600px;margin:auto;">
        <div style="background:linear-gradient(135deg,#0d1b2e,#1a2744);border-radius:12px;padding:24px;border:1px solid #1e3a5f;margin-bottom:24px;">
            <h1 style="color:white;margin:0;font-size:24px;">FraudShield AI</h1>
            <p style="color:#64748b;margin:4px 0 0 0;">Real-Time Fraud Detection System</p>
        </div>
        <div style="background:#450a0a;border:1px solid #dc2626;border-radius:12px;padding:20px;margin-bottom:20px;">
            <h2 style="color:#fca5a5;margin:0 0 8px 0;">FRAUD ALERT DETECTED</h2>
            <p style="color:#fca5a5;margin:0;font-size:14px;">A suspicious transaction has been flagged by the AI system</p>
        </div>
        <div style="background:#0f172a;border:1px solid #1e3a5f;border-radius:12px;padding:20px;margin-bottom:20px;">
            <h3 style="color:white;margin:0 0 16px 0;">Transaction Details</h3>
            <table style="width:100%;border-collapse:collapse;">
                <tr style="border-bottom:1px solid #1e3a5f;">
                    <td style="color:#64748b;padding:8px 0;">Transaction ID</td>
                    <td style="color:white;text-align:right;">{transaction_data['id']}</td>
                </tr>
                <tr style="border-bottom:1px solid #1e3a5f;">
                    <td style="color:#64748b;padding:8px 0;">Amount</td>
                    <td style="color:#fbbf24;text-align:right;font-weight:bold;">${transaction_data['amount']:,.2f}</td>
                </tr>
                <tr style="border-bottom:1px solid #1e3a5f;">
                    <td style="color:#64748b;padding:8px 0;">Fraud Probability</td>
                    <td style="color:#dc2626;text-align:right;font-weight:bold;">{transaction_data['probability']*100:.1f}%</td>
                </tr>
                <tr style="border-bottom:1px solid #1e3a5f;">
                    <td style="color:#64748b;padding:8px 0;">Alert Level</td>
                    <td style="color:#f97316;text-align:right;">{transaction_data['alert_level']}</td>
                </tr>
                <tr>
                    <td style="color:#64748b;padding:8px 0;">Detected At</td>
                    <td style="color:white;text-align:right;">{datetime.now().strftime("%B %d, %Y %H:%M:%S")}</td>
                </tr>
            </table>
        </div>
        <div style="background:#0f172a;border:1px solid #1e3a5f;border-radius:12px;padding:20px;margin-bottom:20px;">
            <h3 style="color:white;margin:0 0 12px 0;">Recommended Actions</h3>
            <ul style="color:#cbd5e1;margin:0;padding-left:20px;">
                <li style="margin-bottom:8px;">Freeze the associated card immediately</li>
                <li style="margin-bottom:8px;">Contact the cardholder for verification</li>
                <li style="margin-bottom:8px;">Flag transaction for compliance review</li>
                <li>Escalate to fraud investigation team if confirmed</li>
            </ul>
        </div>
        <p style="color:#334155;font-size:12px;text-align:center;margin-top:24px;">
            Automated alert from FraudShield AI — GraphSAGE GNN trained on 590K IEEE-CIS transactions
        </p>
    </div>
    """

    message = Mail(
        from_email=FROM_EMAIL,
        to_emails=to_email,
        subject=subject,
        html_content=html_content
    )

    try:
        sg = SendGridAPIClient(SENDGRID_API_KEY)
        response = sg.send(message)
        return response.status_code == 202
    except Exception as e:
        st.error(f"Email error: {e}")
        return False

@st.cache_data(ttl=60)
def load_recent_fraud():
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
        cursor.execute("""
            SELECT * FROM FRAUD_PREDICTIONS
            WHERE PREDICTION = 'FRAUD'
            ORDER BY TIMESTAMP DESC
            LIMIT 10
        """)
        rows = cursor.fetchall()
        cols = [desc[0] for desc in cursor.description]
        df = pd.DataFrame(rows, columns=cols)
        cursor.close()
        conn.close()
        return df
    except Exception as e:
        st.error(f"Snowflake error: {e}")
        return pd.DataFrame()

col1, col2 = st.columns([1, 1])

with col1:
    st.markdown("#### Send Alert Email")
    to_email = st.text_input("Recipient Email", placeholder="compliance@bank.com")

    st.markdown("**Select a fraud transaction:**")
    fraud_df = load_recent_fraud()

    if not fraud_df.empty:
        selected = st.selectbox(
            "Select transaction",
            options=fraud_df['PREDICTION_ID'].tolist(),
            format_func=lambda x: f"{x[:8]}... — ${fraud_df[fraud_df['PREDICTION_ID']==x]['TRANSACTION_AMOUNT'].values[0]:,.2f}"
        )

        selected_row = fraud_df[fraud_df['PREDICTION_ID'] == selected].iloc[0]

        st.markdown(f"""
        <div style="background:#450a0a;border:1px solid #dc2626;border-radius:8px;padding:16px;margin-top:12px;">
            <p style="color:#fca5a5;margin:0;"><b>ID:</b> {selected_row['PREDICTION_ID']}</p>
            <p style="color:#fca5a5;margin:4px 0;"><b>Amount:</b> ${selected_row['TRANSACTION_AMOUNT']:,.2f}</p>
            <p style="color:#fca5a5;margin:4px 0;"><b>Fraud Probability:</b> {selected_row['FRAUD_PROBABILITY']*100:.1f}%</p>
            <p style="color:#fca5a5;margin:0;"><b>Alert Level:</b> {selected_row['ALERT_LEVEL']}</p>
        </div>
        """, unsafe_allow_html=True)

        if st.button("Send Fraud Alert Email", use_container_width=True, type="primary"):
            if not to_email:
                st.error("Please enter a recipient email.")
            else:
                with st.spinner("Sending..."):
                    success = send_fraud_alert(to_email, {
                        'id': selected_row['PREDICTION_ID'],
                        'amount': selected_row['TRANSACTION_AMOUNT'],
                        'probability': selected_row['FRAUD_PROBABILITY'],
                        'alert_level': selected_row['ALERT_LEVEL']
                    })
                if success:
                    st.success(f"Alert sent to {to_email}.")
                else:
                    st.error("Failed to send. Check API key.")
    else:
        st.warning("No fraud transactions found yet.")

with col2:
    st.markdown("#### Recent Fraud Alerts")
    if not fraud_df.empty:
        for _, row in fraud_df.iterrows():
            st.markdown(f"""
            <div style="background:#0f172a;border:1px solid #dc2626;border-radius:8px;
                        padding:12px;margin-bottom:8px;">
                <div style="display:flex;justify-content:space-between;">
                    <span style="color:#fca5a5;font-weight:bold;">{row['PREDICTION_ID'][:12]}...</span>
                    <span style="color:#fbbf24;font-weight:bold;">${row['TRANSACTION_AMOUNT']:,.2f}</span>
                </div>
                <div style="display:flex;justify-content:space-between;margin-top:4px;">
                    <span style="color:#64748b;font-size:12px;">{row['ALERT_LEVEL']}</span>
                    <span style="color:#dc2626;font-size:12px;">{row['FRAUD_PROBABILITY']*100:.1f}% fraud prob</span>
                </div>
            </div>
            """, unsafe_allow_html=True)
    else:
        st.info("No fraud transactions detected yet.")