"use client";
import { motion } from "framer-motion";
import type { BoundingBox } from "@/lib/types";

interface AnomalyHighlightProps {
  bbox: BoundingBox;
  severity?: "CRITICAL" | "WARNING" | "NOMINAL";
}

export function AnomalyHighlight({ bbox, severity = "WARNING" }: AnomalyHighlightProps) {
  const color = severity === "CRITICAL" ? "#dc2626" : "#d97706";
  return (
    <motion.div
      className="absolute pointer-events-none"
      style={{
        left: `${bbox.xmin * 100}%`,
        top: `${bbox.ymin * 100}%`,
        width: `${(bbox.xmax - bbox.xmin) * 100}%`,
        height: `${(bbox.ymax - bbox.ymin) * 100}%`,
        border: `2px solid ${color}`,
        boxShadow: `0 0 18px 3px ${color}66, inset 0 0 18px 3px ${color}33`,
        borderRadius: 4,
      }}
      animate={{
        opacity: [0.7, 1, 0.7],
      }}
      transition={{ duration: 2, repeat: Infinity }}
    />
  );
}