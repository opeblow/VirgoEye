"use client";
import { motion } from "framer-motion";
import { GlassCard } from "@/components/shared/GlassCard";

interface ConfidenceGaugeProps {
  value: number;
}

export function ConfidenceGauge({ value }: ConfidenceGaugeProps) {
  const pct = Math.max(0, Math.min(1, value));
  const color = pct >= 0.8 ? "#16a34a" : pct >= 0.5 ? "#d97706" : "#dc2626";
  const angle = pct * 360;

  return (
    <GlassCard className="flex flex-col items-center gap-1 py-4">
      <svg viewBox="0 0 120 120" className="w-24 h-24" width={120} height={120}>
        <circle cx="60" cy="60" r="45" stroke="#e1ece5" strokeWidth="10" fill="none" />
        <motion.circle
          cx="60"
          cy="60"
          r="45"
          stroke={color}
          strokeWidth="10"
          fill="none"
          strokeLinecap="round"
          strokeDasharray={2 * Math.PI * 45}
          initial={{ strokeDashoffset: 2 * Math.PI * 45 }}
          animate={{
            strokeDashoffset: 2 * Math.PI * 45 * (1 - pct),
          }}
          transform="rotate(-90 60 60)"
          transition={{ duration: 0.9 }}
        />
        <text x="60" y="68" textAnchor="middle" className="fill-virgo-text font-mono" fontSize="14" fontWeight="700">
          {(pct * 100).toFixed(0)}%
        </text>
      </svg>
      <div className="text-[10px] font-mono uppercase tracking-wider text-virgo-muted">Confidence</div>
    </GlassCard>
  );
}