"use client";
import { useCallback, useRef, useState } from "react";
import type { SSEEventRaw } from "@/lib/types";
import { parseSSEChunk } from "@/lib/sse-parser";
import { API_BASE } from "@/lib/api";

type SSEStatus = "idle" | "connecting" | "streaming" | "done" | "error";

interface UseSSEStreamOpts {
  onEvent?: (ev: SSEEventRaw) => void;
  onError?: (msg: string) => void;
}

// Decoder is stateful for multi-byte sequences split across chunks, so it
// must persist across read() calls.
const decoder = new TextDecoder();

export function useSSEStream({ onEvent, onError }: UseSSEStreamOpts = {}) {
  const [status, setStatus] = useState<SSEStatus>("idle");
  const [events, setEvents] = useState<SSEEventRaw[]>([]);
  const bufferRef = useRef("");
  const readerRef = useRef<ReadableStreamDefaultReader<Uint8Array> | null>(null);
  const controllerRef = useRef<AbortController | null>(null);

  const abort = useCallback(() => {
    controllerRef.current?.abort();
    controllerRef.current = null;
    readerRef.current?.cancel();
    readerRef.current = null;
    setStatus("done");
  }, []);

  const start = useCallback(
    async (imageBase64: string, domain = "auto", detailLevel = "high", extraReview = false, accessCode = "") => {
      abort();
      bufferRef.current = "";
      setEvents([]);
      setStatus("connecting");

      const controller = new AbortController();
      controllerRef.current = controller;

      try {
        const res = await fetch(`${API_BASE}/v1/analyze`, {
          method: "POST",
          headers: { "Content-Type": "application/json", ...(accessCode ? {"X-Virgo-Access-Code": accessCode} : {}) },
          body: JSON.stringify({
            image_base64: imageBase64,
            domain,
            detail_level: detailLevel,
            extra_review: extraReview,
          }),
          signal: controller.signal,
        });
        if (!res.ok || !res.body) {
          const failure = await res.json().catch(() => ({}));
          throw new Error(typeof failure.detail === "string" ? failure.detail : `Service unavailable (${res.status})`);
        }

        const reader = res.body.getReader();
        readerRef.current = reader;
        setStatus("streaming");

        for (;;) {
          const { done, value } = await reader.read();
          if (done) break;
          const text = decoder.decode(value, { stream: true });
          const { events: parsed, remainder } = parseSSEChunk(
            bufferRef.current,
            text
          );
          bufferRef.current = remainder;
          for (const ev of parsed) {
            setEvents((prev) => [...prev, ev]);
            onEvent?.(ev);
          }
        }
        decoder.decode();
        setStatus("done");
      } catch (err) {
        if (controller.signal.aborted) {
          // Canceled by reset/new-run — not an error to surface.
          return;
        }
        const msg = err instanceof Error ? err.message : String(err);
        setStatus("error");
        onError?.(msg);
      } finally {
        if (controllerRef.current === controller) controllerRef.current = null;
        readerRef.current = null;
      }
    },
    [abort, onEvent, onError]
  );

  return { status, events, start, abort };
}
