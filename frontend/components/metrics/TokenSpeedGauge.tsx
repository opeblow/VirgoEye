"use client";
import { motion } from "framer-motion";
import { GlassCard } from "@/components/shared/GlassCard";

interface TokenSpeedGaugeProps {
  tps: number;
}

const MAX_TPS = 60;

export function TokenSpeedGauge({ tps }: TokenSpeedGaugeProps) {
  const pct = Math.min(1, tps / MAX_TPS);
  const color = pct > 0.8 ? "#16a34a" : pct > 0.5 ? "#84cc16" : "#d97706";
  const angle = pct * 270;

  return (
    <GlassCard className="flex flex-col items-center gap-1 py-4">
      <svg viewBox="0 0 120 120" className="w-24 h-24" width={120} height={120}>
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
        <text x="60" y="68" textAnchor="middle" className="fill-virgo-text font-mono" fontSize="13" fontWeight="700">
          {tps.toFixed(1)}
        </text>
      </svg>
      <div className="text-[10px] font-mono uppercase tracking-wider text-virgo-muted">Tok / sec</div>
    </GlassCard>
  );
}