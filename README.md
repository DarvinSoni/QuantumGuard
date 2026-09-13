<b>QuantumGuard</b>

A crypto-agile, quantum-resistant framework for securing containerized SIEM log pipelines.

QuantumGuard integrates NIST-standardized Post-Quantum Cryptography (PQC) — ML-KEM (FIPS 203) for key encapsulation and ML-DSA (FIPS 204) for digital signatures — into cloud-native log ingestion pipelines, replacing classical RSA/ECC key-wrapping that is vulnerable to "harvest now, decrypt later" attacks.

<u>The Problem</u>

Inter-container SIEM log pipelines commonly rely on classical asymmetric encryption (RSA-2048, ECC) to wrap symmetric session keys before shipping log batches over the network. That's a problem for two reasons:

Harvest now, decrypt later. An adversary who cannot break RSA/ECC today can still record encrypted log traffic now and decrypt it retroactively once a sufficiently powerful quantum computer exists.
Shor's algorithm provides a theoretical polynomial-time method for factoring large integers and solving discrete logarithms on a fault-tolerant quantum computer — the exact hard problems RSA and ECC rely on.

QuantumGuard addresses this by making the crypto layer of the log pipeline agile: able to run classical, post-quantum, or hybrid schemes, and switch between them dynamically as threat conditions or infrastructure constraints change.

<u>The Solution</u>

A sidecar-proxy pattern that sits alongside each log-emitting container, wrapping AES-256-GCM-encrypted log payloads with:

ML-KEM-768 for post-quantum key encapsulation (replacing RSA/ECDH key exchange)
ML-DSA-65 for post-quantum digital signatures on log batches (replacing RSA/ECDSA signing)
Dynamic fallback/switching logic driven by latency, CPU budget, or threat-intel signals

<u>Architecture & Tech Stack</u>

Layer	Technology

Quantum attack simulation	Python, qiskit, qiskit-aer
PQC cryptographic engine	C/C++ liboqs, pyoqs — ML-KEM-768, ML-DSA-65
Container & streaming pipeline	Docker, Kubernetes (sidecar proxy pattern), gRPC streaming, Redis, AES-256-GCM
Analytics & dashboard	Streamlit, Chart.js, Plotly

<u>Roadmap</u>

 Phase 1 — Attack Proof-of-Concept General small-N implementation of Shor's algorithm via Quantum Phase Estimation (Qiskit/Aer), demonstrated end-to-end against a toy-RSA-wrapped SIEM log session key to make the harvest-now-decrypt-later threat concrete. See /phase1.
 Phase 2 — Core Log Encoder gRPC log-streaming sidecar proxy: micro-batches log payloads, signs them with ML-DSA-65, wraps symmetric keys with ML-KEM-768.
 Phase 3 — Dynamic Crypto-Agility Fallback and dynamic algorithm-switching logic triggered by CPU/latency constraints or threat-intelligence feeds.
 Phase 4 — Analytics & UI Real-time Streamlit dashboard: latency comparison (classical vs. PQC), CPU/RAM overhead, QPE circuit visualizations, dynamic crypto-switching controls.
 
<u>Repository Structure</u>

quantumguard/

├── phase1/          # Quantum attack proof-of-concept (Qiskit Shor's algorithm demo)

├── phase2/          # PQC log encoder sidecar (planned)

├── phase3/          # Crypto-agility controller (planned)

├── phase4/          # Streamlit analytics dashboard (planned)

└── README.md

<u>A Note on Scope</u>

QuantumGuard's quantum attack simulations run on classical simulators (Qiskit Aer) against small, toy-scale keys for demonstration and validation purposes. They do not represent a capability against real-world cryptographic key sizes (e.g., RSA-2048), which remain far outside the reach of both classical simulation and current quantum hardware. The goal of this project is to build and validate a defensive, crypto-agile framework ahead of the eventual arrival of cryptographically relevant quantum computers — not to demonstrate an offensive capability.
