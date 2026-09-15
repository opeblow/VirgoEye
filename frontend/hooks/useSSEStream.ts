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

export function useSSEStream({ onEvent, onError }: UseSSEStreamOpts = {}) {
  const [status, setStatus] = useState<SSEStatus>("idle");
  const [events, setEvents] = useState<SSEEventRaw[]>([]);
  const bufferRef = useRef("");
  const readerRef = useRef<ReadableStreamDefaultReader<Uint8Array> | null>(null);

  const abort = useCallback(() => {
    readerRef.current?.cancel();
    readerRef.current = null;
    setStatus("done");
  }, []);

  const start = useCallback(
    async (imageBase64: string, domain = "auto", detailLevel = "high") => {
      bufferRef.current = "";
      setEvents([]);
      setStatus("connecting");

      try {
        const res = await fetch(`${API_BASE}/v1/analyze`, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            image_base64: imageBase64,
            domain,
            detail_level: detailLevel,
          }),
        });
        if (!res.ok || !res.body) throw new Error(`HTTP ${res.status}`);

        const reader = res.body.getReader();
        readerRef.current = reader;
        setStatus("streaming");

        for (;;) {
          const { done, value } = await reader.read();
          if (done) break;
          const text = new TextDecoder().decode(value);
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
        setStatus("done");
      } catch (err) {
        const msg = err instanceof Error ? err.message : String(err);
        setStatus("error");
        onError?.(msg);
      } finally {
        readerRef.current = null;
      }
    },
    [onEvent, onError]
  );

  return { status, events, start, abort };
}
