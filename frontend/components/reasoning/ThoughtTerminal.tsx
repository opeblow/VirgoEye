"use client";
import { useEffect, useRef } from "react";
import { GlassCard } from "@/components/shared/GlassCard";
import { ScanLineEffect } from "./ScanLineEffect";

interface ThoughtTerminalProps {
  text: string;
  streaming: boolean;
}

export function ThoughtTerminal({ text, streaming }: ThoughtTerminalProps) {
  const scrollRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    scrollRef.current?.scrollTo({ top: scrollRef.current.scrollHeight });
  }, [text]);

  return (
    <GlassCard noPad className="overflow-hidden flex flex-col min-h-[300px]">
      <div className="flex items-center gap-2 px-4 py-2 border-b border-virgo-border/60 bg-virgo-panel/95">
        <span className="w-3 h-3 rounded-full bg-virgo-danger/80" />
        <span className="w-3 h-3 rounded-full bg-virgo-warn/80" />
        <span className="w-3 h-3 rounded-full bg-virgo-ok/80" />
        <span className="ml-2 text-xs font-mono text-virgo-muted">
          deliberation :: covt-thought-stream
        </span>
        {streaming && <span className="ml-auto text-[10px] font-mono text-virgo-accent animate-pulse">REC</span>}
      </div>
      <div ref={scrollRef} className="relative flex-1 overflow-y-auto bg-[#062b17] p-4 min-h-[260px]">
        <ScanLineEffect active={streaming} />
        <pre className="whitespace-pre-wrap break-words font-mono text-[13px] leading-relaxed text-emerald-50/90">
          {text || (
            <span className="text-emerald-200/60 italic">
              // Awaiting stream from CoVT deliberator…
            </span>
          )}
          {streaming && <span className="inline-block w-2 h-4 bg-emerald-400 animate-typewriterCursor" />}
        </pre>
      </div>
    </GlassCard>
  );
}