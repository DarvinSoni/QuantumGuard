# QuantumGuard -- Phase 1: Quantum Attack Proof-of-Concept

Demonstrates *why* QuantumGuard's Phase 2-4 work (ML-KEM / ML-DSA sidecar,
crypto-agility, dashboard) is necessary: a working, general small-N
implementation of Shor's algorithm via Quantum Phase Estimation (QPE),
run on Qiskit + Qiskit Aer, applied to a toy RSA-wrapped "SIEM log
session key" to demonstrate the harvest-now-decrypt-later attack chain
end to end.

## Files

| File | Purpose |
|---|---|
| `shor_qpe.py` | Core engine: modular-multiplication permutation unitaries, controlled-U gate construction, the QPE circuit, continued-fraction order extraction, and the classical Shor control loop (`shor_factor`). |
| `toy_rsa.py` | Minimal textbook RSA (deliberately tiny keys) standing in for the classical key-wrap step in the log pipeline. **Not production crypto.** |
| `demo_phase1_attack.py` | End-to-end narrative demo: generate toy RSA keypair -> wrap a session key -> attacker factors the modulus with Shor/QPE -> rebuilds the private key -> decrypts the harvested ciphertext. Writes `phase1_attack_report.json`. |
| `visualize_circuit.py` | Saves `qpe_circuit_small.png` (readable circuit diagram, a=7/N=15) and `measurement_histogram.png` (QPE measurement outcomes for the N=143 case), for reuse in the Phase 4 dashboard. |
| `requirements.txt` | Python dependencies. |

## Running it

```bash
pip install -r requirements.txt
python3 demo_phase1_attack.py       # the attack narrative
python3 visualize_circuit.py        # circuit + histogram images
```

## How the quantum part actually works

1. **Modular multiplication as a permutation matrix.** For coprime `a`,
   `N`, the map `y -> a*y mod N` is a bijection on `{0,...,N-1}`. We
   build its `2^n x 2^n` permutation matrix directly (`modmul_permutation_matrix`),
   padding the space above `N` with the identity.
2. **Controlled-U built as a block matrix, not via gate synthesis.**
   Qiskit's generic `UnitaryGate.control()` tries to *synthesize* a
   gate-level decomposition of the controlled unitary, and that
   synthesis cost explodes once the target register is more than a
   few qubits (in testing, it hung for minutes on an 8-qubit target).
   Since Aer's simulator natively supports arbitrary dense `unitary`
   instructions and applies them by direct matrix contraction, we
   build the controlled block matrix `[[I,0],[0,U]]` ourselves and hand
   Aer the finished matrix -- this is what makes the demo run in ~2-3s
   instead of timing out.
3. **Standard QPE circuit**: Hadamards on the counting register,
   controlled-`U^(2^j)` for each counting qubit, inverse QFT, measure.
4. **Classical post-processing**: continued-fraction expansion of the
   measured phase recovers a candidate order `r`; `gcd(a^(r/2) ± 1, N)`
   gives the factors once `r` is even and `a^(r/2) != -1 mod N`.
   `shor_factor()` wraps this in the standard retry loop over random
   bases `a`.

Verified against the textbook case (`a=7, N=15`, true order 4) and
against the toy-RSA modulus used in the demo (`N=143 = 11 x 13`),
which recovers the correct factors, correct private exponent, and
correctly decrypts the intercepted ciphertext (see the demo output).

## Scope and honesty note -- please keep this framing in any writeup

This is a genuine, general implementation of Shor's algorithm (it isn't
hardcoded to the textbook `N=15` example -- it works for any small `N`
by constructing the actual modular-multiplication unitary). That said:

- **It is a classical simulation of a quantum circuit**, run on Qiskit
  Aer, not real quantum hardware.
- **Simulating the circuit's state costs `O(2^n)` classically**, where
  `n` is the number of qubits needed to represent `N`. That is exactly
  why this cannot scale to RSA-2048 (a 2048-bit modulus) on any
  classical computer -- simulator or otherwise. This demo is tuned to
  moduli of a few hundred (roughly 8-9 target qubits) purely so it
  finishes in seconds.
- **It uses a dense arbitrary-unitary gate for modular multiplication**,
  not a real modular-exponentiation circuit built from elementary
  arithmetic gates (quantum adders/multipliers). That gate-level circuit
  is what a real quantum computer would need, and building/compiling it
  for cryptographic-size numbers is a much larger undertaking in its own
  right, on top of needing a large fault-tolerant quantum computer that
  does not exist today.
- The purpose of Phase 1 is to make the **mechanism** of the
  "harvest now, decrypt later" threat concrete and demonstrable for the
  QuantumGuard team and stakeholders -- not to claim any capability
  against real-world RSA-2048/ECC key sizes. That's the whole reason
  Phase 2 moves to ML-KEM/ML-DSA: their security doesn't rely on the
  integer factorization or discrete-log problems that Shor's algorithm
  attacks.

## Where this plugs into later phases

- **Phase 2** replaces the RSA key-wrap step this demo attacks with
  ML-KEM-768 encapsulation (`liboqs`/`pyoqs`) and signs log batches
  with ML-DSA-65, inside the gRPC sidecar proxy.
- **Phase 4**'s dashboard can embed `qpe_circuit_small.png` and
  `measurement_histogram.png` directly, and can re-run
  `demo_phase1_attack.py`-style comparisons (RSA latency/vulnerability
  vs. ML-KEM latency/resistance) live.
