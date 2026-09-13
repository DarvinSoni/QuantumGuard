'use client';

import React, { useState, useEffect } from 'react';
import { Shield, ShieldAlert, ShieldCheck, Activity, Cpu, Lock, Terminal, Radio } from 'lucide-react';
import { Line, Bar } from 'react-chartjs-2';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  BarElement,
  Title,
  Tooltip,
  Legend,
} from 'chart.js';

ChartJS.register(CategoryScale, LinearScale, PointElement, LineElement, BarElement, Title, Tooltip, Legend);

interface LogEntry {
  id: string;
  timestamp: string;
  source: string;
  event: string;
  payload: string;
  secured: boolean;
}

export default function QuantumGuardDashboard() {
  const [isAttackSimulated, setIsAttackSimulated] = useState(false);
  const [pqcMode, setPqcMode] = useState<'ML-KEM-768' | 'RSA-2048' | 'HYBRID'>('ML-KEM-768');
  const [logs, setLogs] = useState<LogEntry[]>([]);
  const [ingestRate, setIngestRate] = useState(1420);

  // Stream simulation
  useEffect(() => {
    const interval = setInterval(() => {
      const now = new Date();
      const timeStr = now.toTimeString().split(' ')[0] + '.' + now.getMilliseconds();
      const sources = ['192.168.1.104:auth', '10.0.2.15:db-proxy', '172.17.0.2:nginx-ingress'];
      const events = ['AUTH_SUCCESS', 'TLS_HANDSHAKE', 'LOG_INGEST', 'DB_QUERY'];
      const isSecured = pqcMode !== 'RSA-2048';

      const newLog: LogEntry = {
        id: Math.random().toString(36).substring(2, 9),
        timestamp: timeStr,
        source: sources[Math.floor(Math.random() * sources.length)],
        event: events[Math.floor(Math.random() * events.length)],
        payload: isSecured
          ? `PQC_CT[LWE]: ${Array.from({ length: 24 }, () => Math.floor(Math.random() * 16).toString(16)).join('')}`
          : `UNENCRYPTED_TEXT: user_id=admin_102 token=8f9a2b3c`,
        secured: isSecured,
      };

      setLogs((prev) => [newLog, ...prev.slice(0, 7)]);
      setIngestRate(1400 + Math.floor(Math.random() * 80));
    }, 1200);

    return () => clearInterval(interval);
  }, [pqcMode]);

  // Chart Data
  const latencyData = {
    labels: ['Handshake (ms)', 'Encapsulation (ms)', 'Signing (ms)', 'Total Overhead (ms)'],
    datasets: [
      {
        label: 'Classical (RSA-2048)',
        data: [1.2, 0.8, 1.1, 3.1],
        backgroundColor: 'rgba(239, 68, 68, 0.7)',
      },
      {
        label: 'Post-Quantum (ML-KEM-768)',
        data: [0.4, 0.3, 0.9, 1.6],
        backgroundColor: 'rgba(16, 185, 129, 0.7)',
      },
    ],
  };

  return (
    <div className="min-h-screen bg-slate-950 text-slate-100 font-sans p-6">
      {/* Top Header */}
      <header className="flex flex-col md:flex-row md:items-center justify-between pb-6 mb-6 border-b border-slate-800 gap-4">
        <div className="flex items-center gap-3">
          <div className="p-3 bg-cyan-950 border border-cyan-500/30 rounded-xl">
            <Shield className="w-8 h-8 text-cyan-400" />
          </div>
          <div>
            <h1 className="text-2xl font-bold tracking-tight text-white flex items-center gap-2">
              QUANTUM<span className="text-cyan-400">GUARD</span>
              <span className="text-xs px-2 py-0.5 bg-cyan-500/10 text-cyan-400 border border-cyan-500/20 rounded">
                v0.1-PQC
              </span>
            </h1>
            <p className="text-xs text-slate-400">Post-Quantum Container Logging Proxy • NIST FIPS 203 Target</p>
          </div>
        </div>

        {/* Dynamic Controls */}
        <div className="flex items-center gap-3 bg-slate-900/80 p-2 rounded-xl border border-slate-800">
          <label className="text-xs text-slate-400 pl-2">Mode:</label>
          <select
            value={pqcMode}
            onChange={(e) => setPqcMode(e.target.value as any)}
            className="bg-slate-950 text-xs border border-slate-700 rounded-lg px-3 py-1.5 focus:outline-none focus:border-cyan-500"
          >
            <option value="ML-KEM-768">Strict PQC (ML-KEM-768)</option>
            <option value="HYBRID">Hybrid (ML-KEM + RSA)</option>
            <option value="RSA-2048">Legacy (RSA-2048 Only)</option>
          </select>

          <button
            onClick={() => setIsAttackSimulated(!isAttackSimulated)}
            className={`px-3 py-1.5 rounded-lg text-xs font-semibold flex items-center gap-2 border transition-all ${
              isAttackSimulated
                ? 'bg-rose-500/10 text-rose-400 border-rose-500/40 animate-pulse'
                : 'bg-slate-800 text-slate-300 border-slate-700 hover:bg-slate-700'
            }`}
          >
            <ShieldAlert className="w-3.5 h-3.5" />
            {isAttackSimulated ? 'Shor Attack Active' : 'Simulate Shor Attack'}
          </button>
        </div>
      </header>

      {/* Grid Row 1: KPI Stat Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 mb-6">
        <div className="bg-slate-900/60 border border-slate-800/80 p-4 rounded-xl flex items-center justify-between">
          <div>
            <p className="text-xs text-slate-400 mb-1">Ingestion Throughput</p>
            <p className="text-2xl font-bold text-white tracking-tight">{ingestRate.toLocaleString()} <span className="text-xs text-slate-400 font-normal">msg/s</span></p>
          </div>
          <div className="p-3 bg-blue-500/10 border border-blue-500/20 rounded-lg text-blue-400">
            <Activity className="w-5 h-5" />
          </div>
        </div>

        <div className="bg-slate-900/60 border border-slate-800/80 p-4 rounded-xl flex items-center justify-between">
          <div>
            <p className="text-xs text-slate-400 mb-1">Processing Latency</p>
            <p className="text-2xl font-bold text-emerald-400 tracking-tight">1.62 <span className="text-xs text-slate-400 font-normal">ms</span></p>
          </div>
          <div className="p-3 bg-emerald-500/10 border border-emerald-500/20 rounded-lg text-emerald-400">
            <Cpu className="w-5 h-5" />
          </div>
        </div>

        <div className="bg-slate-900/60 border border-slate-800/80 p-4 rounded-xl flex items-center justify-between">
          <div>
            <p className="text-xs text-slate-400 mb-1">Security State</p>
            <p className={`text-lg font-bold tracking-tight ${pqcMode === 'RSA-2048' || isAttackSimulated ? 'text-rose-400' : 'text-cyan-400'}`}>
              {pqcMode === 'RSA-2048' || isAttackSimulated ? 'VULNERABLE' : 'PQC PROTECTED'}
            </p>
          </div>
          <div className={`p-3 rounded-lg border ${pqcMode === 'RSA-2048' || isAttackSimulated ? 'bg-rose-500/10 border-rose-500/20 text-rose-400' : 'bg-cyan-500/10 border-cyan-500/20 text-cyan-400'}`}>
            {pqcMode === 'RSA-2048' || isAttackSimulated ? <ShieldAlert className="w-5 h-5" /> : <ShieldCheck className="w-5 h-5" />}
          </div>
        </div>

        <div className="bg-slate-900/60 border border-slate-800/80 p-4 rounded-xl flex items-center justify-between">
          <div>
            <p className="text-xs text-slate-400 mb-1">Standard Enforced</p>
            <p className="text-lg font-bold text-indigo-400 tracking-tight">{pqcMode}</p>
          </div>
          <div className="p-3 bg-indigo-500/10 border border-indigo-500/20 rounded-lg text-indigo-400">
            <Lock className="w-5 h-5" />
          </div>
        </div>
      </div>

      {/* Grid Row 2: Live Streams & Analytics */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Real-time SIEM Log Stream (2 Cols) */}
        <div className="lg:col-span-2 bg-slate-900/50 border border-slate-800 rounded-xl p-5 flex flex-col">
          <div className="flex items-center justify-between pb-4 border-b border-slate-800 mb-4">
            <div className="flex items-center gap-2">
              <Terminal className="w-4 h-4 text-cyan-400" />
              <h2 className="text-sm font-semibold text-slate-200">Container Log Ingestion Pipeline</h2>
            </div>
            <span className="flex items-center gap-1.5 text-xs text-emerald-400">
              <Radio className="w-3 h-3 animate-pulse" /> Live Feed
            </span>
          </div>

          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs font-mono">
              <thead>
                <tr className="text-slate-500 border-b border-slate-800/60">
                  <th className="pb-2">TIMESTAMP</th>
                  <th className="pb-2">AGENT SOURCE</th>
                  <th className="pb-2">EVENT</th>
                  <th className="pb-2">ENCRYPTED PAYLOAD</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-800/40">
                {logs.map((log) => (
                  <tr key={log.id} className="hover:bg-slate-800/20 transition-colors">
                    <td className="py-2.5 text-slate-400">{log.timestamp}</td>
                    <td className="py-2.5 text-cyan-300/80">{log.source}</td>
                    <td className="py-2.5">
                      <span className="px-2 py-0.5 rounded bg-slate-800 text-slate-300 font-sans font-medium text-[10px]">
                        {log.event}
                      </span>
                    </td>
                    <td className={`py-2.5 ${log.secured ? 'text-slate-400' : 'text-rose-400 font-semibold'}`}>
                      {log.payload}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>

        {/* Cryptographic Latency Benchmark (1 Col) */}
        <div className="bg-slate-900/50 border border-slate-800 rounded-xl p-5">
          <h2 className="text-sm font-semibold text-slate-200 mb-1">Latency Benchmark</h2>
          <p className="text-xs text-slate-400 mb-4">Execution time comparison (RSA vs. ML-KEM)</p>

          <div className="h-64">
            <Bar
              data={latencyData}
              options={{
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                  legend: { labels: { color: '#94a3b8', font: { size: 10 } } },
                },
                scales: {
                  x: { ticks: { color: '#64748b', font: { size: 9 } }, grid: { display: false } },
                  y: { ticks: { color: '#64748b', font: { size: 9 } }, grid: { color: '#1e293b' } },
                },
              }}
            />
          </div>
        </div>
      </div>
    </div>
  );
}