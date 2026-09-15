"use client";
import { useCallback, useReducer, useRef } from "react";
import { useSSEStream } from "./useSSEStream";
import type {
  PipelineStage,
  DiagnosticMap,
  VerificationReport,
  FinalVerdict,
  PerformanceMetrics,
  SSEEventRaw,
} from "@/lib/types";

export interface PipelineState {
  stage: PipelineStage;
  mapData: DiagnosticMap | null;
  thoughtText: string;
  criticData: VerificationReport | null;
  verdict: FinalVerdict | null;
  metrics: PerformanceMetrics | null;
  error: string | null;
  imagePreviewUrl: string | null;
  imageBase64: string | null;
  startedAt: number | null;
}

const INITIAL: PipelineState = {
  stage: "idle",
  mapData: null,
  thoughtText: "",
  criticData: null,
  verdict: null,
  metrics: null,
  error: null,
  imagePreviewUrl: null,
  imageBase64: null,
  startedAt: null,
};

type Action =
  | { type: "START"; imageUrl: string; base64: string }
  | { type: "EVENT"; ev: SSEEventRaw }
  | { type: "DONE" }
  | { type: "ERROR"; msg: string }
  | { type: "RESET" };

function reducer(s: PipelineState, a: Action): PipelineState {
  switch (a.type) {
    case "RESET":
      return { ...INITIAL };
    case "START":
      return {
        ...INITIAL,
        stage: "mapping",
        imagePreviewUrl: a.imageUrl,
        imageBase64: a.base64,
        startedAt: Date.now(),
      };
    case "DONE":
      return { ...s, stage: "done" };
    case "ERROR":
      return { ...s, stage: "error", error: a.msg };
    case "EVENT": {
      const ev = a.ev;
      if (ev.type === "error") {
        return { ...s, stage: "error", error: ev.message ?? "unknown" };
      }
      if (ev.stage === "mapping" && ev.type === "stage_result") {
        return { ...s, mapData: ev.data as unknown as DiagnosticMap };
      }
      if (ev.stage === "deliberation" && ev.type === "thought") {
        return { ...s, thoughtText: s.thoughtText + (ev.chunk ?? "") };
      }
      if (ev.stage === "deliberation" && ev.type === "stage_result") {
        return { ...s, stage: "critic" };
      }
      if (ev.stage === "critic" && ev.type === "stage_result") {
        return {
          ...s,
          criticData: ev.data as unknown as VerificationReport,
          stage: "synthesis",
        };
      }
      if (ev.stage === "synthesis" && ev.type === "stage_result") {
        return { ...s, verdict: ev.data as unknown as FinalVerdict };
      }
      if (ev.stage === "metrics" && ev.type === "metrics") {
        // Metrics mark completion — but an error is terminal and must win.
        if (s.stage === "error") return s;
        return {
          ...s,
          metrics: ev.data as unknown as PerformanceMetrics,
          stage: "done",
        };
      }
      // chunk events just keep the stage as-is
      return s;
    }
  }
}

export function useDiagnosticPipeline() {
  const [state, dispatch] = useReducer(reducer, INITIAL);

  const onEvent = useCallback(
    (ev: SSEEventRaw) => dispatch({ type: "EVENT", ev }),
    []
  );
  const onError = useCallback(
    (msg: string) => dispatch({ type: "ERROR", msg }),
    []
  );
  const { status, start: sseStart, abort } = useSSEStream({
    onEvent,
    onError,
  });

  const start = useCallback(
    (imageBase64: string, domain = "auto") => {
      const url = `data:image/jpeg;base64,${imageBase64}`;
      dispatch({ type: "START", imageUrl: url, base64: imageBase64 });
      sseStart(imageBase64, domain, "high");
    },
    [sseStart]
  );

  const reset = useCallback(() => {
    abort();
    dispatch({ type: "RESET" });
  }, [abort]);

  return { state, status, start, abort, reset };
}
