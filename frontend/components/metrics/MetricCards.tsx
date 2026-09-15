"use client";
import { LatencyGauge } from "./LatencyGauge";
import { TokenSpeedGauge } from "./TokenSpeedGauge";
import { VRAMGauge } from "./VRAMGauge";
import { ConfidenceGauge } from "./ConfidenceGauge";
import type { PerformanceMetrics, FinalVerdict } from "@/lib/types";

interface MetricCardsProps {
  metrics: PerformanceMetrics | null;
  verdict: FinalVerdict | null;
}

export function MetricCards({ metrics, verdict }: MetricCardsProps) {
  return (
    <div className="grid grid-cols-2 lg:grid-cols-4 gap-3">
      <LatencyGauge ms={metrics?.total_latency_ms ?? 0} />
      <TokenSpeedGauge tps={metrics?.tokens_per_second ?? 0} />
      <VRAMGauge
        used={metrics?.vram_usage_mb ?? 0}
        total={metrics?.vram_total_mb ?? 8192}
      />
      <ConfidenceGauge value={verdict?.confidence ?? 0} />
    </div>
  );
}