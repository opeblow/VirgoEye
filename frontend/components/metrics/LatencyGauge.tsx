"use client";
import { motion } from "framer-motion";
import { GlassCard } from "@/components/shared/GlassCard";

interface LatencyGaugeProps {
  ms: number;
}

function desc(n: number) {
  const pct = Math.min(1, n / 2000);
  return { pct, color: pct > 0.8 ? "#dc2626" : pct > 0.5 ? "#d97706" : "#16a34a" };
}

export function LatencyGauge({ ms }: LatencyGaugeProps) {
  const { pct, color } = desc(ms);
  const angle = pct * 270; // 270° arc
  const label = ms >= 1000 ? `${(ms / 1000).toFixed(2)}s` : `${Math.round(ms)}ms`;

  return (
    <GaugeShell label="Total Latency" value={label} color={color}>
      <svg viewBox="0 0 120 120" className="w-full" width={120} height={120}>
        <path
          d="M 60 60 m 0 -45 a 45 45 0 1 1 -0.01 0"
          stroke="#e1ece5"
          strokeWidth="10"
          fill="none"
          strokeLinecap="round"
          transform="rotate(135 60 60)"
        />
        <motion.path
          d="M 60 60 m 0 -45 a 45 45 0 1 1 -0.01 0"
          stroke={color}
          strokeWidth="10"
          fill="none"
          strokeLinecap="round"
          transform="rotate(135 60 60)"
          initial={{ pathLength: 0 }}
          animate={{ pathLength: angle / 270 }}
          transition={{ duration: 0.8 }}
        />
        <text x="60" y="68" textAnchor="middle" className="fill-virgo-text font-mono" fontSize="14" fontWeight="700">
          {label}
        </text>
      </svg>
    </GaugeShell>
  );
}

function GaugeShell({ label, value, color, children }: { label: string; value: string; color: string; children: React.ReactNode }) {
  return (
    <GlassCard className="flex flex-col items-center gap-1 py-4">
      <div className="w-24 h-24">{children}</div>
      <div className="mt-1 text-[10px] font-mono uppercase tracking-wider text-virgo-muted">{label}</div>
      <div className="font-mono text-sm" style={{ color }}>{value}</div>
    </GlassCard>
  );
}