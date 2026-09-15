"use client";
import { motion } from "framer-motion";
import { STAGE_LABELS, STAGE_COLORS, STAGE_ORDER } from "@/lib/constants";
import type { PipelineStage } from "@/lib/types";
import { cn } from "@/lib/utils";

interface StageIndicatorProps {
  stage: PipelineStage;
}

export function StageIndicator({ stage }: StageIndicatorProps) {
  const currentIdx = STAGE_ORDER.indexOf(stage as (typeof STAGE_ORDER)[number]);

  return (
    <div className="flex items-center justify-between gap-2 w-full">
      {STAGE_ORDER.map((s, i) => {
        const done = currentIdx > i;
        const active = currentIdx === i;
        const color = STAGE_COLORS[s];
        return (
          <div key={s} className="flex-1 flex flex-col items-center gap-2 relative">
            <div className="w-full h-1 rounded-full bg-virgo-border/60 overflow-hidden relative">
              {done && <motion.div className="h-full" style={{ background: color }} />}
              {active && (
                <motion.div
                  className="h-full"
                  style={{ background: color }}
                  animate={{ x: ["-100%", "0%"] }}
                  transition={{ duration: 1.2, repeat: Infinity, ease: "easeInOut" }}
                />
              )}
            </div>
            <div className="flex items-center gap-1.5">
              <span
                className={cn(
                  "w-5 h-5 rounded-full flex items-center justify-center text-[10px] font-mono border",
                  active && "animate-pulse"
                )}
                style={{
                  background: done || active ? color : "transparent",
                  borderColor: color,
                  color: done || active ? "#ffffff" : color,
                }}
              >
                {done ? "✓" : i + 1}
              </span>
              <span
                className={cn(
                  "text-[10px] font-mono hidden sm:block",
                  active || done ? "text-virgo-text" : "text-virgo-dim"
                )}
                style={{ color: active || done ? color : undefined }}
              >
                {STAGE_LABELS[s]}
              </span>
            </div>
          </div>
        );
      })}
    </div>
  );
}