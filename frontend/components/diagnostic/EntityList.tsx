"use client";
import type { DetectedEntity } from "@/lib/types";
import { cn } from "@/lib/utils";
import { GlassCard } from "@/components/shared/GlassCard";

interface EntityListProps {
  entities: DetectedEntity[];
  hoveredId: string | null;
  selectedId: string | null;
  onHover: (id: string | null) => void;
  onSelect: (id: string) => void;
}

export function EntityList({
  entities,
  hoveredId,
  selectedId,
  onHover,
  onSelect,
}: EntityListProps) {
  return (
    <GlassCard noPad className="overflow-hidden">
      <div className="px-4 py-2 border-b border-virgo-border/60 text-xs font-mono text-virgo-muted flex items-center justify-between">
        <span>Detected Entities</span>
        <span className="text-virgo-accent">{entities.length.toString().padStart(2, "0")}</span>
      </div>
      <ul className="max-h-64 overflow-y-auto divide-y divide-virgo-border/40">
        {entities.map((e) => (
          <li
            key={e.id}
            onMouseEnter={() => onHover(e.id)}
            onMouseLeave={() => onHover(null)}
            onClick={() => onSelect(e.id)}
            className={cn(
              "px-4 py-2 text-xs cursor-pointer flex items-center justify-between hover:bg-virgo-accent/5 transition-colors",
              selectedId === e.id && "bg-virgo-accent/10 border-l-2 border-l-virgo-accent"
            )}
          >
            <div className="flex items-center gap-2 min-w-0">
              <span className="font-mono text-virgo-accent shrink-0">{e.id}</span>
              <span className="text-virgo-text truncate">{e.label}</span>
            </div>
            <div className="flex items-center gap-2 shrink-0">
              <span
                className={cn(
                  "h-2 w-2 rounded-full",
                  e.category === "anomaly" ? "bg-virgo-danger" : "bg-virgo-dim"
                )}
              />
              <span className="font-mono text-[10px] text-virgo-muted w-10 text-right">
                {(e.confidence * 100).toFixed(0)}%
              </span>
            </div>
          </li>
        ))}
        {entities.length === 0 && (
          <li className="px-4 py-6 text-center text-xs text-virgo-muted">
            No entities mapped yet
          </li>
        )}
      </ul>
    </GlassCard>
  );
}