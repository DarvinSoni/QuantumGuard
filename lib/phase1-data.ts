import reportJson from "@/files/phase1_attack_report.json";

export type Phase1Report = {
  keypair: { N: number; e: number; bit_length: number };
  intercepted: { ciphertext: number };
  attack_success: boolean;
  recovered_factors: number[];
  order_finding_attempts: Array<{
    attempt: number;
    a: number;
    estimated_order: number;
    top_measurements: [string, number][];
  }>;
  recovered_d: number;
  decryption_matches_original: boolean;
};

export const phase1Report = reportJson as Phase1Report;

/** Stand-in session-key integer used by files/demo_phase1_attack.py (42 % N). */
export const SESSION_KEY_STUB = 42;

export const PHASE1_STEPS = [
  {
    id: 1,
    title: "Sidecar wrap key",
    body: "The SIEM sidecar generates a toy RSA keypair and uses the public modulus to wrap a per-batch session key before shipping logs over gRPC.",
  },
  {
    id: 2,
    title: "Harvest now",
    body: "An adversary records the RSA-wrapped session key plus the encrypted log batch. The ciphertext sits in archive until a later quantum factoring capability exists.",
  },
  {
    id: 3,
    title: "QPE order finding",
    body: "Shor’s algorithm via quantum phase estimation is simulated on Qiskit Aer against the public modulus N. Continued fractions recover a candidate order r from the measured phase.",
  },
  {
    id: 4,
    title: "Rebuild private exponent",
    body: "From the recovered factors p and q, φ(N)=(p−1)(q−1) and d ≡ e⁻¹ (mod φ) reconstruct the RSA private exponent.",
  },
  {
    id: 5,
    title: "Decrypt later",
    body: "The harvested wrap is decrypted with the recovered d. The AES session-key stub matches the original, so every log entry it protected is exposed.",
  },
] as const;

export const SCALE_NOTE =
  "This dashboard shows a recorded laptop simulation of a quantum circuit for a toy modulus (N=143, 8 bits), not real quantum hardware and not RSA-2048. Simulation cost is O(2ⁿ) in the qubits needed to represent N. Modular multiplication is a dense unitary, not a cryptographic-size arithmetic gate circuit. The point is the harvest-now-decrypt-later mechanism — which is why Phase 2 replaces RSA wrap with ML-KEM-768 and signs with ML-DSA-65.";
