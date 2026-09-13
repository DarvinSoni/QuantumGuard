"""
QuantumGuard - Phase 1: Toy RSA for the vulnerability demo
==============================================================

toy_rsa.py

A deliberately tiny, textbook (non-padded, non-production) RSA
implementation used ONLY to stand in for the classical asymmetric
key-wrapping step in a SIEM log pipeline ("Container A encrypts a
session key with the receiver's RSA public key before shipping logs
over gRPC"). The modulus is intentionally small (tens of bits) so that
Shor's algorithm can be run against it on a classical quantum simulator
in seconds.

Do NOT reuse this module as real cryptography anywhere. Real RSA-2048
keys are ~2048 bits; this demo's whole point is that a small-N toy
mirrors the *mechanism* of the attack, not that it says anything about
the practical security margin of real key sizes today.
"""

from __future__ import annotations

import random
from dataclasses import dataclass

from shor_qpe import egcd, is_probable_prime, modinv


def _random_prime(bit_lo: int, bit_hi: int, rng: random.Random) -> int:
    while True:
        candidate = rng.randrange(1 << bit_lo, 1 << bit_hi) | 1
        if is_probable_prime(candidate):
            return candidate


@dataclass
class ToyRSAKeyPair:
    p: int
    q: int
    N: int
    e: int
    d: int


def generate_toy_keypair(bit_lo: int = 3, bit_hi: int = 6, seed: int = 1) -> ToyRSAKeyPair:
    """
    Generate a toy RSA keypair with primes in [2^bit_lo, 2^bit_hi).
    Default range keeps N small enough (typically < 200) for the QPE
    demo to stay fast, while still being a genuine two-distinct-prime
    RSA modulus.
    """
    rng = random.Random(seed)
    p = _random_prime(bit_lo, bit_hi, rng)
    q = _random_prime(bit_lo, bit_hi, rng)
    while q == p:
        q = _random_prime(bit_lo, bit_hi, rng)

    N = p * q
    phi = (p - 1) * (q - 1)

    e = 3
    import math
    while math.gcd(e, phi) != 1:
        e += 2

    d = modinv(e, phi)
    return ToyRSAKeyPair(p=p, q=q, N=N, e=e, d=d)


def encrypt_int(m: int, e: int, N: int) -> int:
    if m >= N:
        raise ValueError("message integer must be < N for this toy scheme")
    return pow(m, e, N)


def decrypt_int(c: int, d: int, N: int) -> int:
    return pow(c, d, N)


def rebuild_private_key(N: int, e: int, p: int, q: int) -> int:
    """Given a recovered factorization of N, reconstruct the private exponent d."""
    if p * q != N:
        raise ValueError("p * q != N -- not a valid factorization")
    phi = (p - 1) * (q - 1)
    return modinv(e, phi)
