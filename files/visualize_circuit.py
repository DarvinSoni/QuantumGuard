"""
QuantumGuard - Phase 1: Circuit & Results Visualization
===========================================================

visualize_circuit.py

Generates static image artifacts that Phase 4's Streamlit dashboard can
later embed directly:
  - qpe_circuit_small.png   : circuit diagram for a small, readable case
                              (a=7, N=15) -- good for slides/docs.
  - measurement_histogram.png : histogram of QPE measurement outcomes for
                              the N=143 case used in the attack demo.

Run:
    python3 visualize_circuit.py
"""

from __future__ import annotations

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

from shor_qpe import build_qpe_circuit, find_order_via_qpe


def save_circuit_diagram() -> None:
    qc = build_qpe_circuit(a=7, N=15, n_count=4, n_target=4)
    fig = qc.draw(output="mpl", fold=-1)
    fig.savefig("qpe_circuit_small.png", dpi=160, bbox_inches="tight")
    plt.close(fig)
    print("Saved qpe_circuit_small.png  (QPE circuit, a=7, N=15, 4 counting qubits)")


def save_measurement_histogram() -> None:
    result = find_order_via_qpe(a=8, N=143, n_count=8, shots=4096, seed=123)
    counts = result.measured_bitstrings
    top = sorted(counts.items(), key=lambda kv: -kv[1])[:12]
    labels = [k for k, _ in top]
    values = [v for _, v in top]

    fig, ax = plt.subplots(figsize=(9, 4.5))
    ax.bar(labels, values, color="#3b82f6")
    ax.set_xlabel("Measured counting-register bitstring")
    ax.set_ylabel("Counts")
    ax.set_title(f"QPE measurement outcomes -- a={result.a}, N={result.N} "
                 f"(estimated order r={result.estimated_order})")
    plt.xticks(rotation=60, ha="right")
    fig.tight_layout()
    fig.savefig("measurement_histogram.png", dpi=160)
    plt.close(fig)
    print("Saved measurement_histogram.png  (QPE outcomes, a=8, N=143)")


if __name__ == "__main__":
    save_circuit_diagram()
    save_measurement_histogram()
