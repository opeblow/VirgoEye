/* ---- Stage names, colors, severity helpers ---- */

import type { Severity } from "./types";

export const STAGE_LABELS: Record<string, string> = {
  mapping: "Spatial Mapping",
  deliberation: "CoVT Deliberation",
  critic: "Critic Verification",
  synthesis: "Final Verdict",
};

export const STAGE_ORDER = ["mapping", "deliberation", "critic", "synthesis"] as const;

export const STAGE_COLORS: Record<string, string> = {
  mapping: "#16a34a",
  deliberation: "#84cc16",
  critic: "#d97706",
  synthesis: "#059669",
};

export const SEVERITY_COLORS: Record<Severity, string> = {
  CRITICAL: "#dc2626",
  WARNING: "#d97706",
  NOMINAL: "#16a34a",
};

export const SEVERITY_BG: Record<Severity, string> = {
  CRITICAL: "rgba(220,38,38,0.10)",
  WARNING: "rgba(217,119,6,0.10)",
  NOMINAL: "rgba(22,163,74,0.10)",
};

export const CATEGORY_ICONS: Record<string, string> = {
  component: "Cpu",
  connection: "Link",
  trace: "GitBranch",
  structure: "Box",
  anomaly: "AlertTriangle",
  text: "Type",
  region: "Square",
};
