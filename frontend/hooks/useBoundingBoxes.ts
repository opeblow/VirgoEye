"use client";
import { useCallback, useState } from "react";
import type { DetectedEntity, BoundingBox } from "@/lib/types";

export function useBoundingBoxes(entities: DetectedEntity[] | null) {
  const [hoveredId, setHoveredId] = useState<string | null>(null);
  const [selectedId, setSelectedId] = useState<string | null>(null);

  const selected = entities?.find((e) => e.id === selectedId) ?? null;

  const onEntityHover = useCallback((id: string | null) => setHoveredId(id), []);
  const onEntityClick = useCallback(
    (id: string) => setSelectedId((prev) => (prev === id ? null : id)),
    []
  );

  return { hoveredId, selectedId, selected, onEntityHover, onEntityClick };
}
