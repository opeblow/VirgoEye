"use client";
import { useEffect, useState } from "react";
import { Header } from "@/components/layout/Header";
import { Footer } from "@/components/layout/Footer";
import { ImageUploader } from "@/components/diagnostic/ImageUploader";
import { DiagnosticCanvas } from "@/components/diagnostic/DiagnosticCanvas";
import { EntityList } from "@/components/diagnostic/EntityList";
import { ThoughtTerminal } from "@/components/reasoning/ThoughtTerminal";
import { StageIndicator } from "@/components/reasoning/StageIndicator";
import { CriticReport } from "@/components/reasoning/CriticReport";
import { VerdictCard } from "@/components/reasoning/VerdictCard";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { GlassCard } from "@/components/shared/GlassCard";
import { useDiagnosticPipeline } from "@/hooks/useDiagnosticPipeline";
import { useBoundingBoxes } from "@/hooks/useBoundingBoxes";
import { useGPUMetrics } from "@/hooks/useGPUMetrics";
import type { DetectedEntity } from "@/lib/types";
import { downloadInspectionReport } from "@/lib/report";
import { API_BASE } from "@/lib/api";

type Domain =
  | "auto"
  | "satellite"
  | "agriculture"
  | "wildlife"
  | "disaster"
  | "pcb"
  | "medical"
  | "architecture";

const DOMAINS: Domain[] = ["agriculture", "satellite", "wildlife", "disaster"];

export default function Dashboard() {
  const { state, status, start, reset } = useDiagnosticPipeline();
  const gpu = useGPUMetrics();
  const [extraReview, setExtraReview] = useState(false);
  const [accessCode, setAccessCode] = useState("");
  const [sampleError, setSampleError] = useState("");
  const [loadingSample, setLoadingSample] = useState(false);
  const [domain, setDomain] = useState<Domain>("agriculture");
  const [health, setHealth] = useState<{ model: string; demo_mode: boolean; provider?: string; access_code_required?: boolean } | null>(null);
  const [elapsed, setElapsed] = useState(0);
  const [connectionError, setConnectionError] = useState(false);
  const [loadedB64, setLoadedB64] = useState<string | null>(null);

  useEffect(() => {
    fetch(`${API_BASE}/v1/health`)
      .then((r) => { if (!r.ok) throw new Error("Service unavailable"); return r.json(); })
      .then(setHealth)
      .catch(() => setConnectionError(true));
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

  useEffect(() => {
    if (!processing || !state.startedAt) return;
    const update = () => setElapsed(Math.floor((Date.now() - state.startedAt!) / 1000));
    update(); const timer = setInterval(update, 1000);
    return () => clearInterval(timer);
  }, [processing, state.startedAt]);

  const begin = () => {
    if (loadedB64 && !processing) start(loadedB64, domain, extraReview, accessCode);
  };

  const useSample = async (name: string) => {
    if (processing || loadingSample) return;
    setLoadingSample(true); setSampleError("");
    try {
      const response = await fetch(`/samples/${name}.jpg`);
      if (!response.ok) throw new Error("Sample unavailable. Please upload an image instead.");
      const blob = await response.blob();
      const b64 = await new Promise<string>((resolve, reject) => {
        const reader = new FileReader(); reader.onerror = reject;
        reader.onload = () => resolve(String(reader.result).split(",")[1]); reader.readAsDataURL(blob);
      });
      setDomain("agriculture"); setLoadedB64(b64);
      start(b64, "agriculture", extraReview, accessCode);
    } catch { setSampleError("Could not load the sample. Please upload an image instead."); }
    finally { setLoadingSample(false); }
  };

  return (
    <div className="h-screen flex flex-col bg-virgo-bg">
      <Header model={health?.model} demoMode={health?.demo_mode} />

      <main className="flex-1 min-h-0 p-4 overflow-auto">
        <section className="rounded-2xl bg-[#123d2b] text-white p-6 md:p-8 mb-5">
          <p className="text-xs uppercase tracking-[0.2em] text-emerald-200">VirgoEye / Field intelligence</p>
          <h1 className="text-3xl md:text-4xl font-semibold mt-3">See the concern. Plan the next check.</h1>
          <p className="text-sm text-emerald-50/80 mt-3 max-w-2xl">Turn a crop image into visible observations, approximate image regions, and practical inspection steps. Built to support your judgment.</p>
          <div className="mt-5 flex flex-wrap gap-3 text-xs text-emerald-100">
            <span>01 Upload a field image</span><span>02 Review the evidence</span><span>03 Take the report to the field</span>
          </div>
        </section>
        <p className="text-xs text-virgo-muted mb-4">{health?.provider === "anthropic" ? "Cloud analysis: running an inspection sends this image to Anthropic. Upload only images you intend to share with that service." : "Check the model status before running an inspection."} Regions are approximate; results are not a confirmed diagnosis.</p>
        {state.metrics && <p className="text-xs text-virgo-muted mb-3">{state.metrics.synthetic ? "Simulated result · no model inference" : state.metrics.cached_stages?.length ? `Earlier model results reused for ${state.metrics.cached_stages.length} stages · ${state.metrics.model_name}` : `Analysis completed in ${(state.metrics.total_latency_ms / 1000).toFixed(1)} seconds · ${state.metrics.model_name}`}</p>}

        <div className="mt-4">
          <GlassCard noPad className="p-4">
            <StageIndicator stage={state.stage} extraReview={extraReview} />
          </GlassCard>
        </div>

        {connectionError && <p role="alert" className="mt-4 text-sm text-virgo-danger">The analysis service is unavailable. Restart the service and reload this page.</p>}
        {processing && <div role="status" aria-live="polite" className="mt-4 rounded-xl border border-virgo-border p-4 text-sm">
          <p className="font-medium">{state.stage === "mapping" ? "Locating meaningful regions…" : state.stage === "deliberation" ? "Reading visible evidence…" : state.stage === "critic" ? "Checking the observations…" : "Preparing your inspection report…"}</p>
          <p className="mt-1 text-xs text-virgo-muted">{elapsed}s elapsed · Keep this page open. Timing varies with the image and model.</p>
        </div>}
        {health?.demo_mode && (
          <div className="mt-4">
            <GlassCard noPad className="px-4 py-2 border border-virgo-accent2/50 bg-virgo-accent2/5 flex flex-wrap items-center gap-x-3 gap-y-1">
              <span className="text-[10px] font-mono uppercase tracking-wider text-virgo-accent2">
                Synthetic UI demonstration
              </span>
              <span className="text-[10px] font-mono text-virgo-muted">
                Simulation mode. These results illustrate the interface and cannot assess crop health.
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

        <section className="mt-5 rounded-2xl border border-virgo-border p-4">
          <h2 className="font-semibold text-sm">Try an example</h2>
          <p className="text-xs text-virgo-muted mt-1">Examples use real model analysis; repeat images may reuse earlier results. The image label is not sent to the model.</p>
          <div className="grid grid-cols-3 gap-3 mt-3">{[
            ["healthy", "Healthy-labelled leaf"], ["affected", "Leaf with visible damage"], ["unclear", "Too blurry to assess"],
          ].map(([name,label]) => <button key={name} onClick={() => useSample(name)} disabled={processing || loadingSample || !health || (!!health.access_code_required && !accessCode)} className="text-left rounded-xl border border-virgo-border bg-white p-2 disabled:opacity-40 hover:border-virgo-accent">
            <img src={`/samples/${name}.jpg`} alt="" className="h-20 w-full rounded-lg object-cover"/>
            <span className="block text-xs font-medium mt-2">{label}</span>
          </button>)}</div>
          <p className="text-[11px] text-virgo-muted mt-3">PlantVillage · Mohanty, Hughes &amp; Salathé · CC BY-SA 3.0. The unclear sample was deliberately blurred. <a href="/samples/ATTRIBUTION.md" className="underline">Sources and license</a></p>
          {sampleError && <p role="alert" className="text-xs text-virgo-danger mt-2">{sampleError}</p>}
        </section>
        <div className="mt-4 flex flex-wrap gap-4 items-center">
          <label className="flex items-center gap-2 text-sm"><input type="checkbox" checked={extraReview} onChange={e => { setExtraReview(e.target.checked); reset(); }} disabled={processing}/> Additional automated review</label>
          <span className="text-xs text-virgo-muted">Optional. Adds time; our small test did not show better outcome categories.</span>
          {health?.access_code_required && <label className="text-sm">Judge access code <input type="password" autoComplete="off" value={accessCode} onChange={e => setAccessCode(e.target.value)} className="ml-2 border rounded-lg p-2 bg-white"/></label>}
        </div>
        <div className="mt-4 grid grid-cols-1 lg:grid-cols-12 gap-4">
          {/* Left rail: upload + entity list */}
          <div className="lg:col-span-3 flex flex-col gap-4">
            <ImageUploader
              imagePreviewUrl={loadedB64 ? `data:image/jpeg;base64,${loadedB64}` : null}
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
              {DOMAINS.map((d) => (
                <button
                  key={d}
                  disabled={processing}
                  onClick={() => { setDomain(d); reset(); }}
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
              disabled={processing || loadingSample || !loadedB64 || !health || (!!health.access_code_required && !accessCode)}
              className="w-full"
            >
              {processing ? "RUNNING…" : state.stage === "done" ? "RUN AGAIN" : "INSPECT IMAGE"}
            </Button>
            {state.stage === "done" && (
              <div className="flex items-center justify-between px-1">
                <Badge tone={state.verdict?.review_status === "needs_review" ? "warning" : "success"}>{state.verdict?.review_status === "needs_review" ? "Needs review" : "Complete"}</Badge>
                <span className="text-[10px] font-mono text-virgo-muted">
                  {state.verdict?.summary.substring(0, 40)}
                </span>
              </div>
            )}

            {state.verdict && <Button onClick={() => {
              const report = { exported_at: new Date().toISOString(), domain, model: health?.model,
                provider: health?.provider, synthetic: health?.demo_mode, image: loadedB64 ? `data:image/jpeg;base64,${loadedB64}` : null,
                observations: state.thoughtText, regions: state.mapData, review: state.criticData, finding: state.verdict,
                metrics: state.metrics };
              downloadInspectionReport(report);
            }}>Download inspection report</Button>}
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
                    <div className="mt-3 px-3 py-2 text-xs text-virgo-muted">
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
            {state.verdict && <VerdictCard verdict={state.verdict} />}
            <details open={processing} className="rounded-xl border border-virgo-border p-3">
              <summary className="cursor-pointer text-sm font-medium">Evidence and analysis details</summary>
              <div className="mt-3 space-y-3">
                <ThoughtTerminal text={state.thoughtText} streaming={processing} />
                {state.criticData && <CriticReport report={state.criticData} />}
              </div>
            </details>
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