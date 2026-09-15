"use client";
import { useRef } from "react";
import type { DetectedEntity, BoundingBox, Severity } from "@/lib/types";
import { BoundingBoxOverlay } from "./BoundingBoxOverlay";
import { AnomalyHighlight } from "./AnomalyHighlight";

interface DiagnosticCanvasProps {
  imageUrl: string;
  entities: DetectedEntity[] | null;
  hoveredId: string | null;
  selectedId: string | null;
  onEntityHover: (id: string | null) => void;
  onEntityClick: (id: string) => void;
  anomalyEntity?: { entity: DetectedEntity; bbox: BoundingBox } | null;
  anomalySeverity?: Severity;
  loading?: boolean;
}

export function DiagnosticCanvas({
  imageUrl,
  entities,
  hoveredId,
  selectedId,
  onEntityHover,
  onEntityClick,
  anomalyEntity,
  anomalySeverity = "WARNING",
  loading,
}: DiagnosticCanvasProps) {
  const wrapRef = useRef<HTMLDivElement>(null);

  return (
    <div
      ref={wrapRef}
      className="relative w-full h-full flex items-center justify-center select-none"
    >
      <div className="relative max-w-full max-h-full">
        <img
          src={imageUrl}
          alt="Diagnostic"
          className="max-w-full max-h-[65vh] object-contain rounded-lg shadow-2xl"
          draggable={false}
        />
        {entities?.map((e) => (
          <BoundingBoxOverlay
            key={e.id}
            entity={e}
            hovered={hoveredId === e.id}
            selected={selectedId === e.id}
            onHover={onEntityHover}
            onClick={onEntityClick}
          />
        ))}
        {anomalyEntity && (
          <AnomalyHighlight bbox={anomalyEntity.bbox} severity={anomalySeverity} />
        )}
        {loading && (
          <div className="absolute inset-0 pointer-events-none">
            <div className="absolute inset-x-0 h-px bg-virgo-accent shadow-[0_0_12px_2px_rgba(22,163,74,0.6)] animate-scanline" />
          </div>
        )}
      </div>
    </div>
  );
}