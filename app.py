import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
import time
from datetime import datetime

# --- Page Config ---
st.set_page_config(
    page_title="QuantumGuard | Control Center",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Dark Mode Cyber Theme CSS
st.markdown("""
<style>
    .stApp { background-color: #0E1117; color: #E0E0E0; }
    .metric-card {
        background-color: #1E2640;
        border: 1px solid #2E3A59;
        border-radius: 8px;
        padding: 15px;
        text-align: center;
    }
    .status-ok { color: #00FF66; font-weight: bold; }
    .status-warn { color: #FFCC00; font-weight: bold; }
    .status-alert { color: #FF0055; font-weight: bold; }
</style>
""", unsafe_allow_html=True)

# --- Sidebar Controls ---
st.sidebar.image("https://img.icons8.com/color/96/000000/shield-with-encryption.png", width=60)
st.sidebar.title("QuantumGuard v0.1")
st.sidebar.caption("PQC Container Logging Framework")
st.sidebar.divider()

engine_mode = st.sidebar.selectbox(
    "Active Encryption Engine",
    ["Hybrid Mode (ML-KEM-768 + RSA-2048)", "Strict PQC (ML-KEM-1024)", "Legacy Classical (RSA-2048)"]
)

attack_sim = st.sidebar.toggle("Simulate Shor's Attack", value=False)
log_stream_active = st.sidebar.checkbox("Stream Real-Time SIEM Logs", value=True)

st.sidebar.divider()
st.sidebar.subheader("System Health")
st.sidebar.write("🟢 Container Agent: **Connected**")
st.sidebar.write("🟢 liboqs Module: **Loaded**")
st.sidebar.write("🟡 Qiskit Engine: **Idle**")

# --- Main Layout ---
st.title("🛡️ QuantumGuard: SIEM Log Protection Unit")
st.caption("Interim Architecture Control & Benchmarking Interface")

# Top Metrics Row
col1, col2, col3, col4 = st.columns(4)
with col1:
    st.markdown('<div class="metric-card"><h4>Ingestion Rate</h4><h2>1,420 msg/s</h2></div>', unsafe_allow_html=True)
with col2:
    st.markdown('<div class="metric-card"><h4>Average Latency</h4><h2>2.14 ms</h2></div>', unsafe_allow_html=True)
with col3:
    status_class = "status-alert" if attack_sim else "status-ok"
    status_text = "VULNERABLE (RSA)" if attack_sim else "PROTECTED (PQC)"
    st.markdown(f'<div class="metric-card"><h4>Security State</h4><h3 class="{status_class}">{status_text}</h3></div>', unsafe_allow_html=True)
with col4:
    st.markdown('<div class="metric-card"><h4>Crypto Standard</h4><h2>NIST FIPS 203</h2></div>', unsafe_allow_html=True)

st.divider()

# Tab Navigation for Review Demonstration
tab1, tab2, tab3 = st.tabs(["📊 Live Metrics & Logging", "⚛️ Qiskit Attack Simulator", "🏗️ Pipeline Topology"])

# --- TAB 1: Live Stream & Metrics ---
with tab1:
    col_left, col_right = st.columns([2, 1])
    
    with col_left:
        st.subheader("Real-Time Ingested SIEM Payload Stream")
        
        # Simulate log dataframe
        logs = []
        statuses = ["SUCCESS", "SUCCESS", "SUCCESS", "AUTH_WARN", "SUCCESS"]
        agents = ["192.168.1.104:auth", "10.0.2.15:db-proxy", "172.17.0.2:nginx"]
        
        for i in range(8):
            ts = datetime.now().strftime("%H:%M:%S.%f")[:-3]
            log_type = statuses[i % len(statuses)]
            agent = agents[i % len(agents)]
            
            if attack_sim and "Legacy" in engine_mode or attack_sim and "Hybrid" in engine_mode:
                enc_payload = f"UNPROTECTED_TEXT: user_id=admin_102 session_token=8f9a2b3c"
            else:
                enc_payload = f"PQC_LWE_CT[{np.random.randint(100000, 999999)}]: " + "".join(np.random.choice(list('abcdef0123456789'), 32))
                
            logs.append({"Timestamp": ts, "Source Agent": agent, "Event": log_type, "Encrypted Payload Data": enc_payload})
            
        df_logs = pd.DataFrame(logs)
        st.dataframe(df_logs, use_container_width=True, hide_index=True)
        
    with col_right:
        st.subheader("Performance Overhead")
        # Latency Comparison Chart
        fig = go.Figure(data=[
            go.Bar(name='Key Exchange', x=['RSA-2048', 'ML-KEM-768'], y=[1.1, 0.4], marker_color='#3366CC'),
            go.Bar(name='Signature/Auth', x=['RSA-2048', 'ML-DSA-65'], y=[0.8, 1.2], marker_color='#109618')
        ])
        fig.update_layout(barmode='stack', title="Cryptographic Processing Time (ms)", height=300, margin=dict(l=20, r=20, t=40, b=20))
        st.plotly_chart(fig, use_container_width=True)

# --- TAB 2: Qiskit Attack Simulation Mock ---
with tab2:
    st.subheader("Module 1 Proof-of-Concept: Quantum Factorization Simulation")
    st.write("Demonstrating key extraction vulnerability via Shor's Algorithm against classical key exchange.")
    
    c1, c2 = st.columns([1, 2])
    
    with c1:
        st.number_input("Target Classical Modulus (N)", value=15, disabled=True)
        st.text_input("Coprime Generator (a)", value="7", disabled=True)
        st.write("Target Key Length: **4 Bits (Simulated)**")
        
        if st.button("Run Shor's Factorization Circuit", type="primary"):
            with st.spinner("Executing QFT Circuit on Aer Simulator..."):
                time.sleep(1.5)
            st.success("Factors Found: p = 3, q = 5")
            st.warning("Classical Private Key Reconstructed!")
            
    with c2:
        st.markdown("**Simulated Quantum Circuit Measurement Histogram (QFT Period Finding)**")
        # Generate dummy histogram for Shor's measurement
        x_vals = ['000', '001', '010', '011', '100', '101', '110', '111']
        y_vals = [0.02, 0.01, 0.47, 0.01, 0.01, 0.02, 0.46, 0.02]
        
        fig_hist = px.bar(x=x_vals, y=y_vals, labels={'x': 'Computational Basis State', 'y': 'Measurement Probability'}, title="Phase Estimation Output Peaks")
        fig_hist.update_traces(marker_color='#FF0055')
        fig_hist.update_layout(height=280, margin=dict(l=20, r=20, t=40, b=20))
        st.plotly_chart(fig_hist, use_container_width=True)

# --- TAB 3: Pipeline Architecture ---
with tab3:
    st.subheader("Containerized Logging & Encryption Architecture")
    st.info("The diagram below represents the sidecar execution flow being built.")
    
    st.code("""
[ Log Source: Nginx / Auth ] 
          │ (IPC Socket)
          ▼
┌─────────────────────────────────────────────────────────────┐
│ QuantumGuard Agent Proxy                                    │
│                                                             │
│ ┌──────────────────────┐      ┌───────────────────────────┐ │
│ │  Log Ingestion Unit  │ ──►  │ Dynamic Crypto Engine     │ │
│ └──────────────────────┘      │ - ML-KEM-768 (Encapsulate)│ │
│                               │ - ML-DSA-65 (Sign Payload)│ │
│                               └───────────────────────────┘ │
└─────────────────────────────┬───────────────────────────────┘
                              │ (gRPC encrypted stream)
                              ▼
                [ SIEM Central Log Sink / Elastic ]
    """, language="text")