"use client";
import Link from "next/link";
import { PulsingDot } from "@/components/shared/PulsingDot";
import { cn } from "@/lib/utils";

interface HeaderProps {
  model?: string;
  demoMode?: boolean;
}

export function Header({ model, demoMode }: HeaderProps) {
  return (
    <header className="flex items-center justify-between px-6 py-3 border-b border-virgo-border/60 bg-virgo-panel/90 backdrop-blur-md">
      <Link href="/" className="flex items-center gap-3 group">
        <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-virgo-accent to-virgo-accent2 flex items-center justify-center">
          <span className="text-white font-bold text-sm">VE</span>
        </div>
        <h1 className="text-lg font-semibold tracking-tight font-sans text-virgo-text">
          VIRGO<span className="text-virgo-accent">-EYE</span>
        </h1>
        <span className="text-xs text-virgo-muted font-mono">v2.0</span>
      </Link>
      <div className="flex items-center gap-4 text-xs font-mono text-virgo-muted">
        {model && (
          <span className="hidden sm:inline">
            {demoMode && (
              <span className="text-virgo-warn mr-2">[DEMO]</span>
            )}
            {model}
          </span>
        )}
        <PulsingDot color={demoMode ? "amber" : "green"} size="sm" />
      </div>
    </header>
  );
}
