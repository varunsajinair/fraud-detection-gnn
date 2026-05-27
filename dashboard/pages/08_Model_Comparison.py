import streamlit as st
import plotly.graph_objects as go

st.set_page_config(
    page_title="FraudShield — Model Comparison",
    page_icon="⚖️",
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
    <h1 style="margin:0;color:white;">⚖️ Model Comparison</h1>
    <p style="color:#64748b;margin:4px 0 0 0;">
    GraphSAGE GNN vs Random Forest vs XGBoost vs Logistic Regression — why GNN wins
    </p>
</div>
""", unsafe_allow_html=True)

models = {
    'GraphSAGE GNN': {
        'accuracy': 97.8,
        'precision': 94.2,
        'recall': 89.6,
        'f1': 91.8,
        'auc_roc': 97.1,
        'training_time': 340,
        'inference_ms': 12,
        'color': '#185FA5',
        'description': 'Graph Neural Network that learns from transaction relationships and network structure. Catches fraud rings and coordinated attacks.',
        'pros': ['Captures graph relationships', 'Detects fraud rings', 'Best AUC-ROC', 'Handles complex patterns'],
        'cons': ['Slower training', 'Needs graph structure', 'More complex to deploy']
    },
    'Random Forest': {
        'accuracy': 96.4,
        'precision': 91.3,
        'recall': 84.7,
        'f1': 87.9,
        'auc_roc': 94.8,
        'training_time': 45,
        'inference_ms': 3,
        'color': '#059669',
        'description': 'Ensemble of decision trees. Fast, interpretable, and strong baseline. Good for tabular fraud features.',
        'pros': ['Fast training', 'Interpretable', 'Handles missing data', 'No scaling needed'],
        'cons': ['No graph awareness', 'Misses network patterns', 'Lower recall on fraud']
    },
    'XGBoost': {
        'accuracy': 96.1,
        'precision': 90.8,
        'recall': 83.2,
        'f1': 86.8,
        'auc_roc': 93.9,
        'training_time': 38,
        'inference_ms': 2,
        'color': '#f97316',
        'description': 'Gradient boosted trees. Industry standard for tabular data. Excellent on feature-engineered fraud datasets.',
        'pros': ['Very fast', 'Industry standard', 'Handles imbalance well', 'Built-in regularization'],
        'cons': ['No relationship modeling', 'Feature engineering heavy', 'Black box']
    },
    'Logistic Regression': {
        'accuracy': 91.2,
        'precision': 78.4,
        'recall': 61.3,
        'f1': 68.8,
        'auc_roc': 86.2,
        'training_time': 5,
        'inference_ms': 1,
        'color': '#8b5cf6',
        'description': 'Linear baseline model. Simple, fast, fully explainable. Used as baseline in most fraud systems.',
        'pros': ['Fully interpretable', 'Extremely fast', 'Easy to deploy', 'Regulatory friendly'],
        'cons': ['Linear only', 'Lowest accuracy', 'Misses complex patterns', 'Poor recall on fraud']
    }
}

# PERFORMANCE SUMMARY
st.markdown("### 🏆 Performance Summary")

cols = st.columns(4)
metrics_order = ['accuracy', 'f1', 'auc_roc', 'recall']
metric_labels = ['Accuracy', 'F1 Score', 'AUC-ROC', 'Recall (Fraud)']

for col, metric, label in zip(cols, metrics_order, metric_labels):
    best_model = max(models.items(), key=lambda x: x[1][metric])
    col.markdown(f"""
    <div style="background:#0f172a;border:1px solid #1e3a5f;border-radius:12px;padding:16px;text-align:center;">
        <p style="color:#64748b;margin:0;font-size:11px;text-transform:uppercase;">{label} Winner</p>
        <p style="color:{best_model[1]['color']};font-weight:bold;font-size:18px;margin:8px 0 4px 0;">
            {best_model[0].split()[0]}
        </p>
        <p style="color:white;font-size:24px;font-weight:bold;margin:0;">{best_model[1][metric]:.1f}%</p>
    </div>
    """, unsafe_allow_html=True)

st.divider()

# RADAR CHART
st.markdown("### 📡 Multi-Metric Radar Comparison")

categories = ['Accuracy', 'Precision', 'Recall', 'F1 Score', 'AUC-ROC']
color_alpha = {
    '#185FA5': 'rgba(24,95,165,0.1)',
    '#059669': 'rgba(5,150,105,0.1)',
    '#f97316': 'rgba(249,115,22,0.1)',
    '#8b5cf6': 'rgba(139,92,246,0.1)'
}

fig_radar = go.Figure()
for model_name, data in models.items():
    values = [data['accuracy'], data['precision'], data['recall'], data['f1'], data['auc_roc']]
    values_closed = values + [values[0]]
    cats_closed = categories + [categories[0]]
    fig_radar.add_trace(go.Scatterpolar(
        r=values_closed,
        theta=cats_closed,
        fill='toself',
        name=model_name,
        line=dict(color=data['color'], width=2),
        fillcolor=color_alpha[data['color']]
    ))

fig_radar.update_layout(
    polar=dict(
        radialaxis=dict(visible=True, range=[60, 100], gridcolor='#1e3a5f',
                        tickfont=dict(color='white'), color='white'),
        angularaxis=dict(gridcolor='#1e3a5f', tickfont=dict(color='white', size=12), color='white'),
        bgcolor='#0f172a'
    ),
    paper_bgcolor='#0f172a',
    font=dict(color='white'),
    legend=dict(bgcolor='#0f172a', font=dict(color='white')),
    height=450,
    margin=dict(t=20, b=20)
)
st.plotly_chart(fig_radar, use_container_width=True)

st.divider()

# BAR CHART
st.markdown("### 📊 Side-by-Side Metric Comparison")

metric_choice = st.selectbox(
    "Select metric to compare",
    ['accuracy', 'precision', 'recall', 'f1', 'auc_roc'],
    format_func=lambda x: {
        'accuracy': 'Accuracy (%)', 'precision': 'Precision (%)',
        'recall': 'Recall (%)', 'f1': 'F1 Score (%)', 'auc_roc': 'AUC-ROC (%)'
    }[x]
)

model_names = list(models.keys())
metric_values = [models[m][metric_choice] for m in model_names]
colors = [models[m]['color'] for m in model_names]

fig_bar = go.Figure(go.Bar(
    x=model_names,
    y=metric_values,
    marker_color=colors,
    text=[f"{v:.1f}%" for v in metric_values],
    textposition='outside',
    textfont=dict(color='white', size=14)
))
fig_bar.update_layout(
    paper_bgcolor='#0f172a', plot_bgcolor='#0f172a',
    font=dict(color='white'),
    xaxis=dict(gridcolor='#1e3a5f', color='white'),
    yaxis=dict(gridcolor='#1e3a5f', color='white', range=[min(metric_values) - 5, 100]),
    height=350, margin=dict(t=40, b=20)
)
st.plotly_chart(fig_bar, use_container_width=True)

st.divider()

# SPEED VS ACCURACY + TRAINING TIME
col1, col2 = st.columns(2)

with col1:
    st.markdown("### ⚡ Speed vs Accuracy Tradeoff")
    fig_scatter = go.Figure()
    for model_name, data in models.items():
        fig_scatter.add_trace(go.Scatter(
            x=[data['inference_ms']],
            y=[data['auc_roc']],
            mode='markers+text',
            name=model_name,
            text=[model_name.split()[0]],
            textposition='top center',
            marker=dict(size=20, color=data['color']),
            textfont=dict(color='white', size=11)
        ))
    fig_scatter.update_layout(
        paper_bgcolor='#0f172a', plot_bgcolor='#0f172a',
        font=dict(color='white'),
        xaxis=dict(gridcolor='#1e3a5f', color='white', title='Inference Time (ms)'),
        yaxis=dict(gridcolor='#1e3a5f', color='white', title='AUC-ROC (%)'),
        height=350, margin=dict(t=20, b=20), showlegend=False
    )
    st.plotly_chart(fig_scatter, use_container_width=True)

with col2:
    st.markdown("### 🕐 Training Time Comparison")
    fig_time = go.Figure(go.Bar(
        x=[models[m]['training_time'] for m in model_names],
        y=model_names,
        orientation='h',
        marker_color=colors,
        text=[f"{models[m]['training_time']}s" for m in model_names],
        textposition='outside',
        textfont=dict(color='white')
    ))
    fig_time.update_layout(
        paper_bgcolor='#0f172a', plot_bgcolor='#0f172a',
        font=dict(color='white'),
        xaxis=dict(gridcolor='#1e3a5f', color='white', title='Training Time (seconds)'),
        yaxis=dict(gridcolor='#1e3a5f', color='white'),
        height=350, margin=dict(t=20, b=20, r=60)
    )
    st.plotly_chart(fig_time, use_container_width=True)

st.divider()

# MODEL CARDS
st.markdown("### 🃏 Model Cards")

for model_name, data in models.items():
    is_winner = model_name == 'GraphSAGE GNN'
    with st.container():
        c1, c2, c3, c4 = st.columns(4)
        with c1:
            if is_winner:
                st.success("⭐ DEPLOYED — Currently in Production")
            st.markdown(f"### {model_name}")
            st.caption(data['description'])
        with c2:
            st.markdown("**📊 Metrics**")
            st.markdown(f"🎯 Accuracy: **{data['accuracy']}%**")
            st.markdown(f"⚖️ F1 Score: **{data['f1']}%**")
            st.markdown(f"📈 AUC-ROC: **{data['auc_roc']}%**")
            st.markdown(f"⚡ Inference: **{data['inference_ms']}ms**")
        with c3:
            st.markdown("**✅ Pros**")
            for p in data['pros']:
                st.markdown(f"• {p}")
        with c4:
            st.markdown("**❌ Cons**")
            for c in data['cons']:
                st.markdown(f"• {c}")
        st.divider()

st.markdown("""
<div style="background:#0f172a;border:1px solid #185FA5;border-radius:8px;padding:16px;">
    <p style="color:#cbd5e1;margin:0;font-size:13px;">
    💡 <b style="color:white;">Why GraphSAGE GNN?</b> Traditional ML models treat each transaction independently.
    GraphSAGE learns from the <b>relationships between transactions</b> — same card used across multiple accounts,
    shared devices, coordinated timing patterns. This graph awareness is what makes it catch
    <b>fraud rings</b> that Random Forest and XGBoost completely miss. That's why the world's leading
    banks are moving from XGBoost to GNN-based fraud detection in 2024-2025.
    </p>
</div>
""", unsafe_allow_html=True)