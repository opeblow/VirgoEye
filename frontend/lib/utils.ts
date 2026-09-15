import { clsx, type ClassValue } from "clsx";
import { twMerge } from "tailwind-merge";
import type { BoundingBox } from "./types";

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}

/** Scale a normalised bbox [0..1] to pixel coords in a container of given size. */
export function bboxToPixels(
  bbox: BoundingBox,
  imgW: number,
  imgH: number
): { x: number; y: number; w: number; h: number } {
  return {
    x: bbox.xmin * imgW,
    y: bbox.ymin * imgH,
    w: (bbox.xmax - bbox.xmin) * imgW,
    h: (bbox.ymax - bbox.ymin) * imgH,
  };
}

/** Format ms to human-readable. */
export function fmtMs(ms: number): string {
  if (ms < 1000) return `${Math.round(ms)}ms`;
  return `${(ms / 1000).toFixed(2)}s`;
}

export function fmtPct(n: number): string {
  return `${(n * 100).toFixed(1)}%`;
}
