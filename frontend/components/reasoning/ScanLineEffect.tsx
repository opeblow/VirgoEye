"use client";
import { cn } from "@/lib/utils";

interface ScanLineEffectProps {
  active: boolean;
  className?: string;
}

export function ScanLineEffect({ active, className }: ScanLineEffectProps) {
  return (
    <div
      className={cn(
        "pointer-events-none absolute inset-0 overflow-hidden rounded-md",
        className
      )}
    >
      <div
        className="absolute inset-x-0 h-10 bg-gradient-to-b from-transparent via-virgo-accent/15 to-transparent"
        style={{
          animation: active ? "scanline 3.2s linear infinite" : "none",
        }}
      />
    </div>
  );
}