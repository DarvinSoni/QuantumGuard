"""
QuantumGuard - Phase 1: Attack Proof-of-Concept
==================================================

demo_phase1_attack.py

Scenario:
---------
A sidecar proxy in a SIEM log pipeline wraps a per-batch AES-256-GCM
session key with the receiving container's classical RSA public key
before shipping the wrapped key + encrypted log batch over gRPC. An
adversary passively records the wrapped key today ("harvest now"),
and later - once a sufficiently capable quantum computer exists -
factors the RSA modulus with Shor's algorithm, recovers the private
key, unwraps the session key, and decrypts the archived log batch
("decrypt later").

This script reproduces that end-to-end story at toy scale:
  1. Generate a toy RSA keypair (small primes -- see toy_rsa.py for why).
  2. "Encrypt" a stand-in session key with the RSA public key.
  3. Play the attacker: run Shor's algorithm (via Qiskit QPE simulation,
     see shor_qpe.py) against the public modulus N to recover its factors.
  4. Rebuild the RSA private key from the recovered factors.
  5. Decrypt the intercepted ciphertext and show the recovered session key.

Run:
    python3 demo_phase1_attack.py
"""

from __future__ import annotations

import json
import time

from shor_qpe import shor_factor
from toy_rsa import decrypt_int, encrypt_int, generate_toy_keypair, rebuild_private_key


def banner(text: str) -> None:
    print("\n" + "=" * 72)
    print(text)
    print("=" * 72)


def run_demo() -> dict:
    report: dict = {}

    banner("STEP 1 - Sidecar proxy generates an RSA keypair for key-wrapping")
    keypair = generate_toy_keypair(bit_lo=2, bit_hi=4, seed=11)
    print(f"  Public modulus  N = {keypair.N}  ({keypair.N.bit_length()} bits)")
    print(f"  Public exponent e = {keypair.e}")
    print(f"  (private: p={keypair.p}, q={keypair.q}, d={keypair.d} -- kept secret)")
    report["keypair"] = {"N": keypair.N, "e": keypair.e, "bit_length": keypair.N.bit_length()}

    banner("STEP 2 - A per-batch AES session key is wrapped with RSA and shipped")
    session_key_stub = 42 % keypair.N  # stand-in for a real 256-bit AES key
    ciphertext = encrypt_int(session_key_stub, keypair.e, keypair.N)
    print(f"  Plaintext session-key stub : {session_key_stub}")
    print(f"  Wrapped (RSA-encrypted)    : {ciphertext}")
    print("  --> This wrapped key + the encrypted log batch are now sitting")
    print("      in an adversary's 'harvest now' archive, waiting for a future")
    print("      quantum computer.")
    report["intercepted"] = {"ciphertext": ciphertext}

    banner("STEP 3 - ATTACKER: run Shor's algorithm (QPE, Qiskit Aer) against N")
    t0 = time.time()
    result = shor_factor(keypair.N, n_count=8, shots=4096, max_attempts=8, rng_seed=123)
    elapsed = time.time() - t0
    print(f"  Quantum-simulated factoring attempt took {elapsed:.2f}s (classical simulation)")

    if result.factors is None:
        print("  Shor's algorithm did NOT converge on a nontrivial factor this run.")
        report["attack_success"] = False
        return report

    p_found, q_found = result.factors
    print(f"  Recovered factors: N = {p_found} * {q_found}")
    print(f"  (True factors were p={keypair.p}, q={keypair.q})")
    report["attack_success"] = True
    report["recovered_factors"] = [p_found, q_found]
    report["order_finding_attempts"] = result.attempts

    banner("STEP 4 - ATTACKER: rebuild the RSA private key from the factorization")
    d_recovered = rebuild_private_key(keypair.N, keypair.e, p_found, q_found)
    print(f"  Recovered private exponent d = {d_recovered}")
    print(f"  (True private exponent was  d = {keypair.d})")
    report["recovered_d"] = d_recovered

    banner("STEP 5 - ATTACKER: decrypt the intercepted, previously-harvested ciphertext")
    recovered_key = decrypt_int(ciphertext, d_recovered, keypair.N)
    print(f"  Decrypted session-key stub = {recovered_key}")
    print(f"  (Original plaintext was    = {session_key_stub})")
    success = recovered_key == session_key_stub
    print(f"\n  MATCH: {success}  -- the AES session key (and therefore every log")
    print("  entry it protected) is now exposed, years after it was harvested.")
    report["decryption_matches_original"] = success

    banner("TAKEAWAY")
    print("  A classical RSA-wrapped SIEM log pipeline is secure only until an")
    print("  attacker gets a large enough fault-tolerant quantum computer.")
    print("  Any log traffic harvested TODAY is retroactively exposed the day")
    print("  that happens. This is exactly the risk ML-KEM (FIPS 203) key")
    print("  encapsulation and ML-DSA (FIPS 204) signatures (Phase 2) are")
    print("  designed to remove, since their hardness assumptions (structured")
    print("  lattices) are not known to be broken by Shor's algorithm.")

    return report


def scale_honesty_note() -> None:
    banner("SCALE / HONESTY NOTE")
    print("  This demo factors a toy modulus of a few dozen bits in seconds on a")
    print("  laptop, via classical *simulation* of a quantum circuit -- not real")
    print("  quantum hardware. Simulating this circuit's state vector costs")
    print("  O(2^n) classically, so it does NOT scale to RSA-2048 (a 2048-bit")
    print("  modulus) on any classical computer, simulator or otherwise. It also")
    print("  does not use a real modular-exponentiation *gate* circuit, which is")
    print("  the (much larger) building block a real fault-tolerant quantum")
    print("  computer would need. The purpose of this proof-of-concept is to")
    print("  demonstrate the *mechanism* of the harvest-now-decrypt-later threat")
    print("  and validate the QuantumGuard team's understanding of it -- not to")
    print("  claim any capability against real-world key sizes.")


if __name__ == "__main__":
    report = run_demo()
    scale_honesty_note()

    with open("phase1_attack_report.json", "w") as f:
        json.dump(report, f, indent=2, default=str)
    print("\nFull machine-readable report written to phase1_attack_report.json")
