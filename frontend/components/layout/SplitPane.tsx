"use client";
import { cn } from "@/lib/utils";

interface SplitPaneProps {
  left: React.ReactNode;
  right: React.ReactNode;
  className?: string;
}

export function SplitPane({ left, right, className }: SplitPaneProps) {
  return (
    <div
      className={cn(
        "flex h-full min-h-0 divide-x divide-virgo-border/60",
        className
      )}
    >
      <div className="flex-1 min-w-0 overflow-hidden flex flex-col">{left}</div>
      <div className="flex-1 min-w-0 overflow-hidden flex flex-col">{right}</div>
    </div>
  );
}
