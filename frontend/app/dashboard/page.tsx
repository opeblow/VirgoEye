"use client";
import { useEffect, useState } from "react";
import { Header } from "@/components/layout/Header";
import { SplitPane } from "@/components/layout/SplitPane";
import { Footer } from "@/components/layout/Footer";
import { ImageUploader } from "@/components/diagnostic/ImageUploader";
import { DiagnosticCanvas } from "@/components/diagnostic/DiagnosticCanvas";
import { EntityList } from "@/components/diagnostic/EntityList";
import { ThoughtTerminal } from "@/components/reasoning/ThoughtTerminal";
import { StageIndicator } from "@/components/reasoning/StageIndicator";
import { CriticReport } from "@/components/reasoning/CriticReport";
import { VerdictCard } from "@/components/reasoning/VerdictCard";
import { MetricCards } from "@/components/metrics/MetricCards";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { GlassCard } from "@/components/shared/GlassCard";
import { useDiagnosticPipeline } from "@/hooks/useDiagnosticPipeline";
import { useBoundingBoxes } from "@/hooks/useBoundingBoxes";
import { useGPUMetrics } from "@/hooks/useGPUMetrics";
import type { DetectedEntity } from "@/lib/types";
import { API_BASE } from "@/lib/api";

type Domain = "auto" | "pcb" | "medical" | "architecture" | "satellite";

export default function Dashboard() {
  const { state, status, start, reset } = useDiagnosticPipeline();
  const gpu = useGPUMetrics();
  const [domain, setDomain] = useState<Domain>("pcb");
  const [health, setHealth] = useState<{ model: string; demo_mode: boolean } | null>(null);
  const [loadedB64, setLoadedB64] = useState<string | null>(null);

  useEffect(() => {
    fetch(`${API_BASE}/v1/health`)
      .then((r) => r.json())
      .then(setHealth)
      .catch(() => {});
  }, []);

  const boxApi = useBoundingBoxes(state.mapData?.entities ?? null);

  const entityIds = new Set(state.mapData?.entities.map((e) => e.id) ?? []);
  const highlighted = state.verdict?.affected_entities?.find((a) => entityIds.has(a.entity_id)) ?? null;
  const primaryAffected = state.verdict?.affected_entities?.[0] ?? null;
  const suspiciousEntity: DetectedEntity | null =
    (primaryAffected &&
      state.mapData?.entities.find((e) => e.id === primaryAffected.entity_id)) ||
    null;

  const processing =
    status === "connecting" || status === "streaming";

  const begin = () => {
    if (loadedB64 && !processing) start(loadedB64, domain);
  };

  return (
    <div className="h-screen flex flex-col bg-virgo-bg">
      <Header model={health?.model} demoMode={health?.demo_mode} />

      <main className="flex-1 min-h-0 p-4 overflow-auto">
        <MetricCards metrics={state.metrics} verdict={state.verdict} />

        <div className="mt-4">
          <GlassCard noPad className="p-4">
            <StageIndicator stage={state.stage} />
          </GlassCard>
        </div>

        {health?.demo_mode && (
          <div className="mt-4">
            <GlassCard noPad className="px-4 py-2 border border-virgo-accent2/50 bg-virgo-accent2/5 flex flex-wrap items-center gap-x-3 gap-y-1">
              <span className="text-[10px] font-mono uppercase tracking-wider text-virgo-accent2">
                Synthetic UI demonstration
              </span>
              <span className="text-[10px] font-mono text-virgo-muted">
                No live inference — Ollama/vLLM not reachable. Outputs are
                image-aware simulations, not medical/engineering verdicts.
              </span>
            </GlassCard>
          </div>
        )}

        {state.error && (
          <div className="mt-4">
            <GlassCard noPad className="p-4 border border-virgo-danger/60 bg-virgo-danger/5">
              <div className="flex items-start gap-3">
                <span className="text-virgo-danger font-mono text-xs mt-0.5">
                  [error]
                </span>
                <div>
                  <p className="text-sm font-semibold text-virgo-danger">
                    Diagnostic pipeline failed
                  </p>
                  <p className="text-xs font-mono text-virgo-muted mt-1">
                    {state.error}
                  </p>
                </div>
              </div>
            </GlassCard>
          </div>
        )}

        <div className="mt-4 grid grid-cols-1 lg:grid-cols-12 gap-4">
          {/* Left rail: upload + entity list */}
          <div className="lg:col-span-3 flex flex-col gap-4">
            <ImageUploader
              imagePreviewUrl={state.imagePreviewUrl}
              onImageReady={(b64) => {
                setLoadedB64(b64);
                reset();
              }}
              onClear={() => {
                setLoadedB64(null);
                reset();
              }}
              disabled={processing}
            />

            <div className="flex flex-wrap gap-1.5">
              {(["auto", "pcb", "medical", "architecture", "satellite"] as Domain[]).map((d) => (
                <button
                  key={d}
                  onClick={() => setDomain(d)}
                  className={`px-3 py-1 rounded-full text-[10px] font-mono uppercase border transition-colors ${
                    domain === d
                      ? "border-virgo-accent text-virgo-accent bg-virgo-accent/10"
                      : "border-virgo-border text-virgo-muted hover:text-virgo-text"
                  }`}
                >
                  {d}
                </button>
              ))}
            </div>

            <Button
              size="lg"
              onClick={begin}
              disabled={processing || !loadedB64}
              className="w-full"
            >
              {processing ? "RUNNING…" : state.stage === "done" ? "RUN AGAIN" : "RUN DIAGNOSTIC"}
            </Button>
            {state.stage === "done" && (
              <div className="flex items-center justify-between px-1">
                <Badge tone="success">Complete</Badge>
                <span className="text-[10px] font-mono text-virgo-muted">
                  {state.verdict?.summary.substring(0, 40)}
                </span>
              </div>
            )}

            {state.mapData && (
              <EntityList
                entities={state.mapData.entities}
                hoveredId={boxApi.hoveredId}
                selectedId={boxApi.selectedId}
                onHover={boxApi.onEntityHover}
                onSelect={boxApi.onEntityClick}
              />
            )}
          </div>

          {/* Center: diagnostic canvas */}
          <div className="lg:col-span-5">
            <GlassCard noPad className="relative overflow-hidden min-h-[380px] flex items-center justify-center">
              {state.imagePreviewUrl ? (
                <div className="relative p-2 w-full">
                  <DiagnosticCanvas
                    imageUrl={state.imagePreviewUrl}
                    entities={state.mapData?.entities ?? null}
                    hoveredId={boxApi.hoveredId}
                    selectedId={boxApi.selectedId}
                    onEntityHover={boxApi.onEntityHover}
                    onEntityClick={boxApi.onEntityClick}
                    loading={processing}
                    anomalyEntity={suspiciousEntity ? { entity: suspiciousEntity, bbox: highlighted!.bbox } : null}
                    anomalySeverity={state.verdict?.severity}
                  />
                  {state.mapData && (
                    <div className="absolute bottom-3 left-1/2 -translate-x-1/2 px-3 py-1 rounded-full bg-black/70 text-[10px] font-mono text-virgo-muted">
                      {state.mapData.image_context}
                    </div>
                  )}
                </div>
              ) : (
                <p className="text-virgo-dim text-sm font-mono">
                  // upload an image to begin stage 1: spatial mapping
                </p>
              )}
            </GlassCard>
          </div>

          {/* Right: reasoning */}
          <div className="lg:col-span-4 flex flex-col gap-4">
            <ThoughtTerminal text={state.thoughtText} streaming={processing} />
            {state.criticData && <CriticReport report={state.criticData} />}
            {state.verdict && <VerdictCard verdict={state.verdict} />}
          </div>
        </div>
      </main>

      <Footer
        gpuUtil={gpu?.gpu_utilization_percent}
        vramUsed={gpu?.vram_usage_mb}
        vramTotal={gpu?.vram_total_mb}
      />
    </div>
  );
}