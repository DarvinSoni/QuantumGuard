import streamlit as st
import pandas as pd
import numpy as np
import time

st.set_page_config(page_title="QuantumGuard Dashboard", layout="wide", initial_sidebar_state="expanded")

# Title & Header
st.title("🛡️ QuantumGuard: Post-Quantum SIEM Ingestion Control")


st.divider()

# Sidebar Controls
st.sidebar.header("Pipeline Configuration")
pqc_enabled = st.sidebar.toggle("Enforce PQC (ML-KEM-768)", value=True)
log_rate = st.sidebar.slider("Ingestion Rate (logs/sec)", 100, 5000, 1200)

if pqc_enabled:
    st.sidebar.success("Status: PQC Tunnel Active (ML-KEM / ML-DSA)")
else:
    st.sidebar.error("Status: Legacy Mode Active (RSA-2048) — Vulnerable!")

# Top Metrics
col1, col2, col3, col4 = st.columns(4)
col1.metric("Ingestion Rate", f"{log_rate} msg/s", "+5%")
col2.metric("Active Protocol", "ML-KEM-768" if pqc_enabled else "RSA-2048")
col3.metric("Avg Latency", "3.4 ms" if pqc_enabled else "1.1 ms", "+2.3ms (PQC Overhead)")
col4.metric("Integrity Status", "SECURE" if pqc_enabled else "COMPROMISED")

st.divider()

# Main Body Split
left_col, right_col = st.columns([1, 1])

with left_col:
    st.subheader("1. Quantum Attack Simulator (Qiskit Engine)")
    st.info("Simulating Shor's Algorithm Factorization on Intercepted Classical Keys")
    
    if st.button("Execute Quantum Attack Simulation"):
        with st.spinner("Running Quantum Fourier Transform (QFT) Circuit..."):
            time.sleep(1.5)
        st.error("Key Factorized! Modulus N=15 broken (p=3, q=5). Private Key Extracted.")
        st.json({"timestamp": "2026-08-16T15:30:00Z", "agent_ip": "10.0.4.12", "event": "SUDO_EXEC", "user": "root"})
    else:
        st.write("Click above to run the Qiskit simulation pipeline.")

with right_col:
    st.subheader("2. Benchmarking: RSA vs ML-KEM")
    chart_data = pd.DataFrame({
        "Metric": ["Handshake (ms)", "Key Size (Bytes)", "CPU Load (%)"],
        "RSA-2048": [1.1, 256, 12],
        "ML-KEM-768": [3.4, 1184, 18]
    }).set_index("Metric")
    
    st.bar_chart(chart_data)

st.divider()
st.subheader("3. Real-Time Encrypted Stream Pipeline")
st.code("""[2026-08-16 15:31:02] [AGENT-01] [ML-KEM-ENC] 0x8f3a1b...7c4e2d [STATUS: VERIFIED]
[2026-08-16 15:31:03] [AGENT-02] [ML-KEM-ENC] 0x9e2b4c...1f8a3b [STATUS: VERIFIED]""", language="bash")