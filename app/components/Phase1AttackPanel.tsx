"use client";

import type { ReactNode } from "react";
import { Bar } from "react-chartjs-2";
import { AlertTriangle, Binary, KeyRound, Layers, LockKeyhole } from "lucide-react";
import { PHASE1_STEPS, SCALE_NOTE, SESSION_KEY_STUB, phase1Report } from "@/lib/phase1-data";

type Props = {
  attackActive: boolean;
  pqcMode: "ML-KEM-768" | "RSA-2048" | "HYBRID";
  activeStep: number;
};

export default function Phase1AttackPanel({ attackActive, pqcMode, activeStep }: Props) {
  const attempt = phase1Report.order_finding_attempts[0];
  const rsaExposed = attackActive && pqcMode === "RSA-2048";
  const hybridPartial = attackActive && pqcMode === "HYBRID";
  const pqcHolds = attackActive && pqcMode === "ML-KEM-768";

  const histogramData = {
    labels: attempt.top_measurements.map(([bitstring]) => bitstring),
    datasets: [
      {
        label: "QPE shots",
        data: attempt.top_measurements.map(([, count]) => count),
        backgroundColor: "rgba(59, 130, 246, 0.85)",
        borderRadius: 4,
      },
    ],
  };

  return (
    <section className="mt-6 grid grid-cols-1 xl:grid-cols-3 gap-6">
      <div className="xl:col-span-2 bg-slate-900/50 border border-slate-800 rounded-xl p-5">
        <div className="flex items-start justify-between gap-4 pb-4 border-b border-slate-800 mb-4">
          <div>
            <h2 className="text-sm font-semibold text-slate-200">Phase 1 · Harvest-now / decrypt-later (toy RSA)</h2>
            <p className="text-xs text-slate-400 mt-1">
              Recorded Qiskit Aer run from <code className="text-cyan-400">files/demo_phase1_attack.py</code> — N=
              {phase1Report.keypair.N}, e={phase1Report.keypair.e}.
            </p>
          </div>
          <span
            className={`shrink-0 text-[10px] font-semibold px-2 py-1 rounded border ${
              rsaExposed
                ? "bg-rose-500/10 text-rose-400 border-rose-500/40"
                : pqcHolds
                  ? "bg-emerald-500/10 text-emerald-400 border-emerald-500/40"
                  : hybridPartial
                    ? "bg-amber-500/10 text-amber-300 border-amber-500/40"
                    : "bg-slate-800 text-slate-400 border-slate-700"
            }`}
          >
            {rsaExposed
              ? "RSA wrap broken"
              : pqcHolds
                ? "ML-KEM wrap holds"
                : hybridPartial
                  ? "RSA limb exposed"
                  : "Idle"}
          </span>
        </div>

        <ol className="grid grid-cols-1 sm:grid-cols-5 gap-2 mb-5">
          {PHASE1_STEPS.map((step) => {
            const lit = attackActive && activeStep >= step.id;
            return (
              <li
                key={step.id}
                className={`rounded-lg border p-3 text-[11px] transition-colors ${
                  lit ? "border-cyan-500/40 bg-cyan-500/5 text-slate-200" : "border-slate-800 bg-slate-950/40 text-slate-500"
                }`}
              >
                <p className="font-mono text-[10px] text-cyan-500/80 mb-1">STEP {step.id}</p>
                <p className="font-semibold mb-1">{step.title}</p>
                <p className="leading-relaxed">{step.body}</p>
              </li>
            );
          })}
        </ol>

        <div className="grid grid-cols-2 md:grid-cols-4 gap-3 mb-5">
          <Metric icon={<KeyRound className="w-3.5 h-3.5" />} label="Public modulus N" value={String(phase1Report.keypair.N)} hint={`${phase1Report.keypair.bit_length}-bit toy`} />
          <Metric icon={<LockKeyhole className="w-3.5 h-3.5" />} label="Harvested wrap" value={String(phase1Report.intercepted.ciphertext)} hint={`session stub ${SESSION_KEY_STUB}`} />
          <Metric
            icon={<Binary className="w-3.5 h-3.5" />}
            label="Recovered factors"
            value={`${phase1Report.recovered_factors[0]} × ${phase1Report.recovered_factors[1]}`}
            hint={`a=${attempt.a}, r̂=${attempt.estimated_order}`}
          />
          <Metric
            icon={<Layers className="w-3.5 h-3.5" />}
            label="Recovered d / match"
            value={`${phase1Report.recovered_d} / ${phase1Report.decryption_matches_original ? "yes" : "no"}`}
            hint="plaintext unwrap"
          />
        </div>

        <div className="rounded-lg border border-slate-800 bg-slate-950/50 p-3 mb-4">
          <p className="text-[10px] uppercase tracking-wide text-slate-500 mb-2">QPE counting-register outcomes (top shots)</p>
          <div className="h-44">
            <Bar
              data={histogramData}
              options={{
                responsive: true,
                maintainAspectRatio: false,
                plugins: { legend: { display: false } },
                scales: {
                  x: { ticks: { color: "#64748b", font: { size: 8 }, maxRotation: 60 }, grid: { display: false } },
                  y: { ticks: { color: "#64748b", font: { size: 9 } }, grid: { color: "#1e293b" } },
                },
              }}
            />
          </div>
        </div>

        <div className="flex items-start gap-2 text-xs text-slate-400 leading-relaxed bg-amber-500/5 border border-amber-500/20 rounded-lg p-3">
          <AlertTriangle className="w-4 h-4 text-amber-400 shrink-0 mt-0.5" />
          <p>{SCALE_NOTE}</p>
        </div>
      </div>

      <div className="bg-slate-900/50 border border-slate-800 rounded-xl p-5 flex flex-col gap-4">
        <h2 className="text-sm font-semibold text-slate-200">QPE circuit (readable case)</h2>
        <p className="text-xs text-slate-400">
          Diagram equivalent of <code className="text-cyan-400">qpe_circuit_small.png</code> from{" "}
          <code className="text-cyan-400">visualize_circuit.py</code> — a=7, N=15, 4 counting qubits. Controlled-U is the modular-multiply permutation, not a 2048-bit arithmetic circuit.
        </p>
        <QpeSchematic />
        <div className="text-[11px] text-slate-400 space-y-2 mt-auto border-t border-slate-800 pt-4">
          <p>
            <span className="text-slate-200 font-medium">RSA-2048 mode:</span> this recorded factorization unwraps the harvested session key.
          </p>
          <p>
            <span className="text-slate-200 font-medium">ML-KEM-768:</span> wrap hardness is structured lattices; Shor on an integer modulus does not recover the encapsulation.
          </p>
        </div>
      </div>
    </section>
  );
}

function Metric({
  icon,
  label,
  value,
  hint,
}: {
  icon: ReactNode;
  label: string;
  value: string;
  hint: string;
}) {
  return (
    <div className="rounded-lg border border-slate-800 bg-slate-950/40 p-3">
      <p className="flex items-center gap-1.5 text-[10px] text-slate-500 mb-1">
        <span className="text-cyan-400">{icon}</span>
        {label}
      </p>
      <p className="text-sm font-mono text-white">{value}</p>
      <p className="text-[10px] text-slate-500 mt-0.5">{hint}</p>
    </div>
  );
}

function QpeSchematic() {
  const stages = ["H⊗n", "C-U^{2^j}", "IQFT", "Measure"];
  return (
    <div className="rounded-lg border border-slate-800 bg-slate-950 p-4">
      <p className="text-[10px] font-mono text-cyan-400/80 mb-3">counting register → target |1⟩</p>
      <div className="flex items-center gap-1">
        {stages.map((stage, i) => (
          <div key={stage} className="flex items-center gap-1 flex-1">
            <div className="flex-1 text-center text-[10px] font-semibold py-3 rounded-md bg-cyan-500/10 border border-cyan-500/30 text-cyan-200">
              {stage}
            </div>
            {i < stages.length - 1 && <div className="w-3 h-px bg-slate-600" />}
          </div>
        ))}
      </div>
      <p className="text-[10px] text-slate-500 mt-3 leading-relaxed">
        Hadamards on the counting register, controlled modular multiplication {'U^{2^j}'} into the target, inverse QFT, then continued-fraction order extraction.
      </p>
    </div>
  );
}
