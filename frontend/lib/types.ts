/* ---- Back-end schema mirrors (TypeScript) ---- */

export interface BoundingBox {
  xmin: number;
  ymin: number;
  xmax: number;
  ymax: number;
}

export type EntityCategory =
  | "component"
  | "connection"
  | "trace"
  | "structure"
  | "anomaly"
  | "text"
  | "region";

export interface DetectedEntity {
  id: string;
  label: string;
  bbox: BoundingBox;
  confidence: number;
  category: EntityCategory;
  description?: string;
}

export interface DiagnosticMap {
  entities: DetectedEntity[];
  total_entities: number;
  image_context: string;
  scan_coverage: number;
}

export interface ThoughtChunk {
  chunk_id: number;
  text: string;
  referenced_entities: string[];
  reasoning_type: string;
}

export interface ThoughtChain {
  chunks: ThoughtChunk[];
  total_tokens: number;
  reasoning_depth: number;
  entities_analyzed: string[];
  entities_skipped: string[];
}

export interface HallucinationFlag {
  chunk_id: number;
  claim: string;
  issue: string;
  severity: "minor" | "major" | "critical";
}

export interface Correction {
  original_claim: string;
  issue: string;
  corrected_claim: string;
  referenced_entity_id?: string;
}

export interface VerificationReport {
  verified: boolean;
  hallucination_count: number;
  hallucinations: HallucinationFlag[];
  missed_entities: string[];
  corrections: Correction[];
  critic_confidence: number;
  critic_notes: string;
}

export type Severity = "CRITICAL" | "WARNING" | "NOMINAL";

export interface AffectedEntity {
  entity_id: string;
  role: "primary" | "secondary" | "context";
  bbox: BoundingBox;
}

export interface EvidenceStep {
  step_number: number;
  description: string;
  supporting_entity_ids: string[];
}

export interface FinalVerdict {
  image_suitability?: "adequate" | "limited" | "unsuitable";
  visible_concern?: "present" | "absent" | "uncertain";
  review_status?: "reviewed" | "needs_review" | "not_reviewed";
  limitations?: string[];
  primary_finding: string;
  severity: Severity;
  confidence: number;
  affected_entities: AffectedEntity[];
  evidence_chain: EvidenceStep[];
  recommended_action: string;
  summary: string;
}

export interface PerformanceMetrics {
  cached_stages?: string[];
  synthetic?: boolean;
  total_latency_ms: number;
  stage_latencies: Record<string, number>;
  tokens_per_second: number;
  total_tokens_generated: number;
  vram_usage_mb: number;
  vram_total_mb: number;
  gpu_utilization_percent: number;
  model_name: string;
  quantization: string;
  image_resolution: string;
}

/* ---- SSE event shape ---- */

export interface SSEEventRaw {
  type: string;
  stage: string;
  chunk?: string;
  delta?: string;
  clean?: string;
  data?: Record<string, unknown>;
  message?: string;
}

/* ---- Pipeline state exposed to the UI ---- */

export type PipelineStage =
  | "idle"
  | "mapping"
  | "deliberation"
  | "critic"
  | "synthesis"
  | "done"
  | "error";

export interface PipelineState {
  stage: PipelineStage;
  mapData: DiagnosticMap | null;
  thoughtText: string;
  criticData: VerificationReport | null;
  verdict: FinalVerdict | null;
  metrics: PerformanceMetrics | null;
  error: string | null;
  imagePreviewUrl: string | null;
  startedAt: number | null;
}
