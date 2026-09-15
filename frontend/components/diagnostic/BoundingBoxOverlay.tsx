"use client";
import { useState } from "react";
import type { DetectedEntity } from "@/lib/types";
import { cn } from "@/lib/utils";

interface BoundingBoxOverlayProps {
  entity: DetectedEntity;
  hovered: boolean;
  selected: boolean;
  onHover: (id: string | null) => void;
  onClick: (id: string) => void;
}

const CATEGORY_COLORS: Record<string, string> = {
  component: "#16a34a",
  connection: "#84cc16",
  trace: "#4a5568",
  structure: "#0891b2",
  anomaly: "#dc2626",
  text: "#cbd5e1",
  region: "#f59e0b",
};

export function BoundingBoxOverlay({
  entity,
  hovered,
  selected,
  onHover,
  onClick,
}: BoundingBoxOverlayProps) {
  const [localHover, setLocalHover] = useState(false);
  const active = hovered || selected || localHover;
  const { bbox } = entity;
  const color = CATEGORY_COLORS[entity.category] ?? "#16a34a";

  const left = bbox.xmin * 100;
  const top = bbox.ymin * 100;
  const width = (bbox.xmax - bbox.xmin) * 100;
  const height = (bbox.ymax - bbox.ymin) * 100;

  // clamp label above the box top edge
  const labelTop = bbox.ymin * 100 - 2.2;

  return (
    <div
      className="absolute pointer-events-auto cursor-pointer"
      style={{ left: `${left}%`, top: `${top}%`, width: `${width}%`, height: `${height}%` }}
      onMouseEnter={() => {
        setLocalHover(true);
        onHover(entity.id);
      }}
      onMouseLeave={() => {
        setLocalHover(false);
        onHover(null);
      }}
      onClick={(e) => {
        e.stopPropagation();
        onClick(entity.id);
      }}
      title={`${entity.id}: ${entity.label}`}
    >
      <div
        className="w-full h-full rounded-[3px]"
        style={{
          border: `${active ? 2 : 1}px solid ${color}`,
          background: active ? `${color}1f` : "transparent",
          boxShadow: active ? `0 0 10px ${color}66` : "none",
          outline: selected ? `2px dashed ${color}` : "none",
        }}
      />
      {active && (
        <div
          className="absolute left-0 font-mono text-[10px] leading-none whitespace-nowrap px-1 py-0.5 rounded bg-black/80 text-virgo-text"
          style={{ top: `${labelTop}%`, color }}
        >
          {entity.id} · {entity.confidence.toFixed(2)}
        </div>
      )}
    </div>
  );
}