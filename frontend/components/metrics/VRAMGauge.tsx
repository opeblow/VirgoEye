"use client";
import { motion } from "framer-motion";
import { GlassCard } from "@/components/shared/GlassCard";

interface VRAMGaugeProps {
  used: number;
  total: number;
}

export function VRAMGauge({ used, total }: VRAMGaugeProps) {
  const pct = total > 0 ? Math.min(1, used / total) : 0;
  const color = pct > 0.9 ? "#dc2626" : pct > 0.7 ? "#d97706" : "#16a34a";

  return (
    <GlassCard className="flex flex-col items-center gap-2 py-4">
      <div className="flex items-end gap-1 h-20">
        {Array.from({ length: 11 }).map((_, i) => (
          <motion.div
            key={i}
            className="w-2 rounded-sm"
            style={{ background: i / 10 <= pct ? color : "#e1ece5" }}
            initial={{ height: 0 }}
            animate={{ height: `${4 + (i + 1) * 6}px` }}
            transition={{ delay: i * 0.04 }}
          />
        ))}
      </div>
      <div className="text-[10px] font-mono uppercase tracking-wider text-virgo-muted">VRAM</div>
      <div className="font-mono text-sm" style={{ color }}>
        {used > 0 ? `${used.toFixed(0)} / ${total.toFixed(0)} MB` : `— / ${total.toFixed(0)} MB`}
      </div>
    </GlassCard>
  );
}