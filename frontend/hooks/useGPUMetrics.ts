"use client";
import { useEffect, useRef, useState } from "react";
import type { PerformanceMetrics } from "@/lib/types";
import { API_BASE } from "@/lib/api";

export function useGPUMetrics() {
  const [metrics, setMetrics] = useState<PerformanceMetrics | null>(null);
  const intervalRef = useRef<ReturnType<typeof setInterval> | null>(null);

  useEffect(() => {
    let active = true;
    const poll = async () => {
      try {
        const res = await fetch(`${API_BASE}/v1/health`);
        if (res.ok && active) {
          const data = await res.json();
          // health endpoint returns a subset; merge with defaults
          setMetrics((prev) => ({
            total_latency_ms: prev?.total_latency_ms ?? 0,
            stage_latencies: prev?.stage_latencies ?? {},
            tokens_per_second: 0,
            total_tokens_generated: 0,
            vram_usage_mb: data.gpu?.vram_usage_mb ?? 0,
            vram_total_mb: data.gpu?.vram_total_mb ?? 0,
            gpu_utilization_percent: data.gpu?.gpu_utilization_percent ?? 0,
            model_name: data.model ?? "",
            quantization: data.quantization ?? "",
            image_resolution: "",
          }));
        }
      } catch {
        // silent
      }
    };
    poll();
    intervalRef.current = setInterval(poll, 5000);
    return () => {
      active = false;
      if (intervalRef.current) clearInterval(intervalRef.current);
    };
  }, []);

  return metrics;
}
