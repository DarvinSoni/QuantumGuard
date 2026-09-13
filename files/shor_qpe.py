"""
QuantumGuard - Phase 1: Quantum Attack Proof-of-Concept
=========================================================

shor_qpe.py

Implements Shor's algorithm via Quantum Phase Estimation (QPE) for
factoring small integers N, using Qiskit + Qiskit Aer as the classical
simulator of the quantum circuit.

SCOPE & HONESTY NOTE (read before using this in any report):
--------------------------------------------------------------
This builds a *general* modular-multiplication unitary as an explicit
permutation matrix, so it works for any small N (not just the textbook
N=15 case). That generality is what makes it useful as a demo -- and
also exactly why it cannot scale: representing U_a: |y> -> |a*y mod N>
as a dense 2^n x 2^n matrix means simulation cost explodes exponentially
with the bit-length of N. This is a teaching/demo tool for N up to a
few hundred (n_bits ~ 8-9) on a classical simulator, NOT a path to
factoring cryptographic-strength (2048-bit) RSA moduli. Real Shor's
algorithm on real hardware needs a modular-exponentiation circuit built
from arithmetic *gates* (quantum adders/multipliers) acting on ~thousands
of logical qubits with deep fault-tolerant error correction -- a very
different and far larger engineering effort that does not exist today.
Keep this framing in any downstream documentation (see README_phase1.md).
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from fractions import Fraction
from typing import Optional

import numpy as np
from qiskit import QuantumCircuit, transpile
from qiskit.circuit.library import QFT, UnitaryGate
from qiskit_aer import AerSimulator


# ---------------------------------------------------------------------------
# Number theory helpers
# ---------------------------------------------------------------------------

def egcd(a: int, b: int) -> tuple[int, int, int]:
    """Extended Euclidean algorithm. Returns (g, x, y) with a*x + b*y = g."""
    if a == 0:
        return b, 0, 1
    g, x1, y1 = egcd(b % a, a)
    return g, y1 - (b // a) * x1, x1


def modinv(a: int, m: int) -> int:
    g, x, _ = egcd(a % m, m)
    if g != 1:
        raise ValueError(f"{a} has no inverse mod {m}")
    return x % m


def is_probable_prime(n: int) -> bool:
    if n < 2:
        return False
    for p in [2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31]:
        if n % p == 0:
            return n == p
    d, r = n - 1, 0
    while d % 2 == 0:
        d //= 2
        r += 1
    for a in [2, 3, 5, 7, 11, 13, 17]:
        if a >= n:
            continue
        x = pow(a, d, n)
        if x in (1, n - 1):
            continue
        for _ in range(r - 1):
            x = pow(x, 2, n)
            if x == n - 1:
                break
        else:
            return False
    return True


# ---------------------------------------------------------------------------
# Quantum modular-multiplication unitary
# ---------------------------------------------------------------------------

def modmul_permutation_matrix(a: int, N: int, n_bits: int) -> np.ndarray:
    """
    Build the 2^n_bits x 2^n_bits permutation (unitary) matrix implementing
    |y> -> |a*y mod N>  for 0 <= y < N,  and the identity on y >= N
    (the "junk" subspace above N needed to pad to a power of two).

    math.gcd(a, N) must be 1, so this map is a bijection on {0,...,N-1}.
    """
    if math.gcd(a, N) != 1:
        raise ValueError(f"a={a} is not coprime to N={N}")
    dim = 1 << n_bits
    if N > dim:
        raise ValueError("n_bits too small to represent N")
    U = np.zeros((dim, dim), dtype=complex)
    for y in range(dim):
        target = (a * y) % N if y < N else y  # identity outside the [0,N) subspace
        U[target, y] = 1.0
    return U


def controlled_modmul_gate(a: int, power: int, N: int, n_bits: int) -> UnitaryGate:
    """
    Returns a UnitaryGate implementing the *controlled* version of
    |y> -> |a^power * y mod N> directly as a dense block matrix:

        C = |0><0| (x) I_target   +   |1><1| (x) U_target

    We build this by hand instead of calling Qiskit's generic
    UnitaryGate.control(), because the generic path tries to *synthesize*
    a gate-level decomposition of the controlled unitary -- and that
    synthesis cost blows up badly once the target register is more than
    a few qubits (it made building a single controlled gate for an
    8-qubit target register hang for minutes). Aer's simulator natively
    supports arbitrary dense 'unitary' instructions and applies them by
    direct matrix contraction, so handing it the already-assembled block
    matrix skips the expensive synthesis step entirely and is exact.

    Qubit-ordering convention: this gate is meant to be appended as
    qc.append(gate, [control_qubit] + target_qubits), i.e. the control
    qubit is listed first / is the least-significant qubit of the
    combined register, matching Qiskit's little-endian convention.
    """
    a_pow = pow(a, power, N)
    U = modmul_permutation_matrix(a_pow, N, n_bits)
    dim = U.shape[0]
    I = np.eye(dim, dtype=complex)

    # control qubit is the least-significant qubit -> combined index
    # = target_index * 2 + control_bit
    C = np.zeros((2 * dim, 2 * dim), dtype=complex)
    # control = 0 block -> identity on target
    C[0:2 * dim:2, 0:2 * dim:2] = I
    # control = 1 block -> U on target
    C[1:2 * dim:2, 1:2 * dim:2] = U

    label = f"C-M_{a}^{power}_mod{N}"
    return UnitaryGate(C, label=label)


# ---------------------------------------------------------------------------
# QPE-based order finding
# ---------------------------------------------------------------------------

@dataclass
class OrderFindingResult:
    a: int
    N: int
    n_count: int
    n_target: int
    measured_bitstrings: dict[str, int]  # bitstring -> counts
    best_phase_fraction: Optional[Fraction]
    estimated_order: Optional[int]
    circuit: QuantumCircuit


def build_qpe_circuit(a: int, N: int, n_count: int, n_target: int) -> QuantumCircuit:
    """
    Build the QPE circuit that estimates the phase of the eigenvalue of
    U_a: |y> -> |a*y mod N> associated with eigenstate |1>, whose phase is
    k/r for some k coprime-ish to r, where r = ord_N(a) is the multiplicative
    order we want to recover.

    n_count   : number of counting/ancilla qubits (precision of phase estimate)
    n_target  : number of qubits needed to represent values 0..N-1
    """
    qc = QuantumCircuit(n_count + n_target, n_count, name=f"QPE_Shor_a{a}_N{N}")

    counting = list(range(n_count))
    target = list(range(n_count, n_count + n_target))

    # Counting register -> |+>^n_count
    for q in counting:
        qc.h(q)

    # Target register -> |1>  (eigenstate we probe)
    qc.x(target[0])

    # Controlled-U^(2^j) for each counting qubit j (standard QPE construction).
    # controlled_modmul_gate already returns the *controlled* unitary as a
    # single dense block matrix (see its docstring for why we avoid
    # Qiskit's generic .control() synthesis here) -- so we append it
    # directly with the control qubit first.
    for j, q in enumerate(counting):
        power = 1 << j
        gate = controlled_modmul_gate(a, power, N, n_target)
        qc.append(gate, [q] + target)

    # Inverse QFT on the counting register
    qc.append(QFT(n_count, inverse=True).to_gate(label="QFT†"), counting)

    qc.measure(counting, list(range(n_count)))
    return qc


def continued_fraction_order(phase: float, N: int, max_den: Optional[int] = None) -> Optional[Fraction]:
    """Approximate `phase` (in [0,1)) as k/r with r <= N via continued fractions."""
    if max_den is None:
        max_den = N
    frac = Fraction(phase).limit_denominator(max_den)
    return frac


def find_order_via_qpe(
    a: int,
    N: int,
    n_count: int = 10,
    shots: int = 2048,
    seed: Optional[int] = 7,
) -> OrderFindingResult:
    """
    Run the QPE circuit for base `a` mod N on the Aer simulator, and try to
    recover the multiplicative order r = ord_N(a) from the measurement
    statistics via continued-fraction expansion of each measured phase.
    """
    n_target = max(1, math.ceil(math.log2(N)))
    # ensure target register can represent N-1
    while (1 << n_target) < N:
        n_target += 1

    qc = build_qpe_circuit(a, N, n_count, n_target)

    sim = AerSimulator(seed_simulator=seed)
    tqc = transpile(qc, sim)
    job = sim.run(tqc, shots=shots)
    counts = job.result().get_counts()

    # Try every distinct measured bitstring, sorted by frequency, and see
    # which one yields a denominator r such that a^r mod N == 1.
    best_r = None
    best_frac = None
    for bitstring, _ in sorted(counts.items(), key=lambda kv: -kv[1]):
        y = int(bitstring, 2)
        phase = y / (1 << n_count)
        frac = continued_fraction_order(phase, N)
        r_candidate = frac.denominator
        if r_candidate == 0:
            continue
        if pow(a, r_candidate, N) == 1 and r_candidate > 1:
            best_r = r_candidate
            best_frac = frac
            break
        # also try small multiples of the denominator (phase k/r with gcd(k,r)!=1)
        for mult in range(2, 5):
            r_try = r_candidate * mult
            if r_try < N and pow(a, r_try, N) == 1:
                best_r = r_try
                best_frac = frac
                break
        if best_r:
            break

    return OrderFindingResult(
        a=a,
        N=N,
        n_count=n_count,
        n_target=n_target,
        measured_bitstrings=counts,
        best_phase_fraction=best_frac,
        estimated_order=best_r,
        circuit=qc,
    )


# ---------------------------------------------------------------------------
# Full Shor factoring wrapper (classical control loop + quantum subroutine)
# ---------------------------------------------------------------------------

@dataclass
class ShorResult:
    N: int
    factors: Optional[tuple[int, int]]
    a_used: Optional[int]
    order_found: Optional[int]
    attempts: list[dict]


def shor_factor(
    N: int,
    n_count: int = 10,
    shots: int = 2048,
    max_attempts: int = 6,
    rng_seed: int = 42,
) -> ShorResult:
    """
    Classical Shor's-algorithm control loop:
      1. Handle trivial cases (even N, N a prime power) classically.
      2. Pick random a coprime to N.
      3. Use the quantum subroutine (QPE) to estimate the order r = ord_N(a).
      4. If r is even and a^(r/2) != -1 mod N, gcd(a^(r/2)-1, N) and
         gcd(a^(r/2)+1, N) give nontrivial factors.
      5. Retry with a fresh `a` on failure, up to max_attempts.
    """
    import random as _random
    rng = _random.Random(rng_seed)
    attempts_log: list[dict] = []

    if N % 2 == 0:
        return ShorResult(N, (2, N // 2), None, None, attempts_log)
    if is_probable_prime(N):
        return ShorResult(N, None, None, None, attempts_log)  # N itself is prime, nothing to factor

    tried = set()
    for attempt in range(1, max_attempts + 1):
        candidates = [x for x in range(2, N) if math.gcd(x, N) == 1 and x not in tried]
        if not candidates:
            break
        a = rng.choice(candidates)
        tried.add(a)

        g = math.gcd(a, N)
        if g > 1:
            attempts_log.append({"attempt": attempt, "a": a, "note": f"lucky gcd hit: {g}"})
            return ShorResult(N, (g, N // g), a, None, attempts_log)

        result = find_order_via_qpe(a, N, n_count=n_count, shots=shots, seed=rng_seed + attempt)
        r = result.estimated_order

        log_entry = {
            "attempt": attempt,
            "a": a,
            "estimated_order": r,
            "top_measurements": sorted(result.measured_bitstrings.items(), key=lambda kv: -kv[1])[:3],
        }

        if r is None:
            log_entry["note"] = "order-finding failed to converge on this shot batch"
            attempts_log.append(log_entry)
            continue

        if r % 2 != 0:
            log_entry["note"] = "order is odd, cannot use this attempt"
            attempts_log.append(log_entry)
            continue

        x = pow(a, r // 2, N)
        if x == N - 1:
            log_entry["note"] = "a^(r/2) = -1 mod N, non-informative, retrying"
            attempts_log.append(log_entry)
            continue

        p = math.gcd(x - 1, N)
        q = math.gcd(x + 1, N)
        attempts_log.append(log_entry)

        if p not in (1, N) and N % p == 0:
            return ShorResult(N, (p, N // p), a, r, attempts_log)
        if q not in (1, N) and N % q == 0:
            return ShorResult(N, (q, N // q), a, r, attempts_log)

    return ShorResult(N, None, None, None, attempts_log)
