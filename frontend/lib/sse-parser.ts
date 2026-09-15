import type { SSEEventRaw } from "./types";

/**
 * Parse an SSE text chunk into SSEEventRaw[].
 * SSE frames are delimited by blank lines (`\n\n`).
 * Each frame has `event:` and `data:` lines.
 */
export function parseSSEChunk(
  buffer: string,
  chunk: string
): { events: SSEEventRaw[]; remainder: string } {
  const combined = buffer + chunk;
  const frames = combined.split("\n\n");
  const remainder = frames.pop() ?? "";
  const events: SSEEventRaw[] = [];

  for (const frame of frames) {
    const lines = frame.split("\n");
    let eventType = "message";
    let dataLines: string[] = [];

    for (const line of lines) {
      if (line.startsWith("event: ")) {
        eventType = line.slice(7).trim();
      } else if (line.startsWith("data: ")) {
        dataLines.push(line.slice(6));
      } else if (line.startsWith(":")) {
        // comment, skip
      }
    }

    if (dataLines.length === 0) continue;
    const raw = dataLines.join("\n");
    try {
      const parsed = JSON.parse(raw);
      events.push({
        type: parsed.type ?? eventType,
        stage: parsed.stage ?? eventType,
        chunk: parsed.chunk,
        delta: parsed.delta,
        clean: parsed.clean,
        data: parsed.data,
        message: parsed.message,
      });
    } catch {
      events.push({
        type: eventType,
        stage: eventType,
        data: { raw },
      });
    }
  }

  return { events, remainder };
}
