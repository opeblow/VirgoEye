"use client";
import { AlertTriangle } from "lucide-react";
import type { VerificationReport } from "@/lib/types";
import { GlassCard } from "@/components/shared/GlassCard";

interface CriticReportProps {
  report: VerificationReport;
}

export function CriticReport({ report }: CriticReportProps) {
  return (
    <GlassCard>
      <div className="flex items-center justify-between mb-3">
        <h3 className="text-sm font-medium text-virgo-text flex items-center gap-2">
          <AlertTriangle className="w-4 h-4 text-virgo-warn" />
          Automated evidence review
        </h3>
        <span
          className={`text-xs font-mono px-2 py-1 rounded-full ${
            report.verified
              ? "bg-virgo-ok/10 text-virgo-ok"
              : "bg-virgo-danger/10 text-virgo-danger"
          }`}
        >
          {report.verified ? "PASS" : "FAIL"}
        </span>
      </div>

      <div className="grid grid-cols-3 gap-2 mb-3 text-center">
        <Stat label="Flagged claims" value={report.hallucination_count} color="text-virgo-danger" />
        <Stat label="Missed" value={report.missed_entities.length} color="text-virgo-warn" />
        <Stat
          label="Model estimate"
          value={`${(report.critic_confidence * 100).toFixed(0)}%`}
          color="text-virgo-accent"
        />
      </div>

      {report.corrections.length > 0 && (
        <div className="mb-3 space-y-2">
          <p className="text-[10px] font-mono text-virgo-muted uppercase">Corrections</p>
          {report.corrections.map((c, i) => (
            <div key={i} className="rounded-lg border border-virgo-warn/30 bg-virgo-warn/5 p-2 text-[11px] font-mono">
              <div className="text-virgo-danger line-through decoration-wavy">{c.original_claim}</div>
              <div className="text-virgo-ok mt-1">→ {c.corrected_claim}</div>
            </div>
          ))}
        </div>
      )}

      {report.missed_entities.length > 0 && (
        <p className="text-[10px] font-mono text-virgo-muted">
          Missed entities: {report.missed_entities.join(", ")}
        </p>
      )}

      <p className="mt-3 text-xs text-virgo-muted leading-relaxed">{report.critic_notes}</p>
    </GlassCard>
  );
}

function Stat({ label, value, color }: { label: string; value: string | number; color: string }) {
  return (
    <div className="rounded-lg bg-virgo-border/40 border border-virgo-border/50 p-2">
      <div className={`text-lg font-mono font-bold ${color}`}>{value}</div>
      <div className="text-[9px] uppercase tracking-wide text-virgo-dim">{label}</div>
    </div>
  );
}