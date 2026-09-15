"use client";
import type { FinalVerdict } from "@/lib/types";
import { SEVERITY_COLORS, SEVERITY_BG } from "@/lib/constants";
import { GlassCard } from "@/components/shared/GlassCard";

interface VerdictCardProps {
  verdict: FinalVerdict;
}

export function VerdictCard({ verdict }: VerdictCardProps) {
  const color = SEVERITY_COLORS[verdict.severity];
  return (
    <GlassCard className="border-t-4" noPad>
      <div
        className="p-5 border-b border-virgo-border/50"
        style={{ background: SEVERITY_BG[verdict.severity] }}
      >
        <div className="flex items-center justify-between">
          <span
            className="text-[10px] font-mono uppercase tracking-widest"
            style={{ color }}
          >
            Final Verdict
          </span>
          <span
            className="text-2xl font-black font-mono tracking-tight"
            style={{ color }}
          >
            {verdict.severity}
          </span>
        </div>
        <h3 className="text-sm font-medium text-virgo-text mt-2">{verdict.primary_finding}</h3>
      </div>
      <div className="p-5 space-y-4">
        <div className="flex items-center gap-3">
          <span className="text-[10px] font-mono text-virgo-muted uppercase">Confidence</span>
          <div className="flex-1 h-2 rounded-full bg-virgo-border/60 overflow-hidden">
            <div
              className="h-full rounded-full transition-all duration-700"
              style={{ width: `${verdict.confidence * 100}%`, background: color }}
            />
          </div>
          <span className="font-mono text-sm" style={{ color }}>
            {(verdict.confidence * 100).toFixed(1)}%
          </span>
        </div>

        <div>
          <p className="text-[10px] font-mono text-virgo-muted uppercase mb-2">
            Evidence Chain
          </p>
          <ol className="space-y-2">
            {verdict.evidence_chain.map((step) => (
              <li key={step.step_number} className="flex gap-2 text-xs text-virgo-text/90">
                <span className="font-mono text-virgo-accent shrink-0">
                  [{String(step.step_number).padStart(2, "0")}]
                </span>
                <span className="leading-relaxed">{step.description}</span>
              </li>
            ))}
          </ol>
        </div>

        {verdict.affected_entities.length > 0 && (
          <div>
            <p className="text-[10px] font-mono text-virgo-muted uppercase mb-2">
              Affected Entities
            </p>
            <div className="flex flex-wrap gap-2">
              {verdict.affected_entities.map((a) => (
                <span
                  key={a.entity_id}
                  className="px-2 py-1 rounded-full border text-[10px] font-mono"
                  style={{
                    borderColor: color,
                    color,
                    background: `${color}11`,
                  }}
                >
                  {a.entity_id} · {a.role}
                </span>
              ))}
            </div>
          </div>
        )}

        <div className="rounded-lg bg-virgo-border/40 border border-virgo-border/50 p-3">
          <p className="text-[10px] font-mono text-virgo-muted uppercase mb-1">Recommended Action</p>
          <p className="text-xs text-virgo-text leading-relaxed">{verdict.recommended_action}</p>
        </div>
      </div>
    </GlassCard>
  );
}