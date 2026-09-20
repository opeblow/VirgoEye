import type { FinalVerdict, DiagnosticMap, VerificationReport, PerformanceMetrics } from "./types";

type Report = {
  exported_at: string; domain: string; model?: string; provider?: string;
  synthetic?: boolean; image: string | null; observations: string;
  regions: DiagnosticMap | null; review: VerificationReport | null;
  finding: FinalVerdict | null; metrics: PerformanceMetrics | null;
};
const escape = (value: unknown) => String(value ?? "").replace(/[&<>"']/g,
  c => ({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;","'":"&#39;"}[c]!));

export function downloadInspectionReport(report: Report) {
  if (!report.finding) return;
  const finding = report.finding;
  const html = `<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
  <title>VirgoEye inspection report</title><style>body{font:16px/1.6 system-ui;color:#173b2a;max-width:850px;margin:40px auto;padding:0 24px}header{border-bottom:3px solid #173b2a}small{color:#526551}img{max-width:100%;max-height:450px;object-fit:contain}section{margin:28px 0}pre{white-space:pre-wrap;font:inherit}.status{padding:14px;background:#edf2e5}li{margin:8px 0}@media print{body{margin:0}}</style>
  <header><small>VIRGOEYE / FIELD INSPECTION</small><h1>${escape(finding.primary_finding)}</h1>
  <p>${escape(report.domain)} · ${escape(report.exported_at)}</p></header>
  <p class="status">${report.synthetic ? "SIMULATION — not a field assessment" : escape(finding.review_status === "reviewed" ? "Automated review completed; human confirmation required" : finding.review_status === "not_reviewed" ? "Standard inspection — no additional automated review" : "NEEDS HUMAN REVIEW")}</p>
  <small>Provider: ${escape(report.provider)} · Model: ${escape(report.model)} · Visual inspection support, not a confirmed diagnosis.</small>
  ${report.image && /^data:image\/jpeg;base64,[A-Za-z0-9+/=]+$/.test(report.image) ? `<section><img alt="Inspected image" src="${report.image}"></section>` : ""}
  <section><h2>Assessment</h2><p>Visible concern: ${escape(finding.visible_concern ?? "not assessed")} · Image suitability: ${escape(finding.image_suitability ?? "not assessed")}</p></section>
  <section><h2>Next field check</h2><p>${escape(finding.recommended_action)}</p></section>
  <section><h2>Visible evidence and uncertainty</h2><pre>${escape(report.observations)}</pre></section>
  <section><h2>Evidence references</h2><ol>${finding.evidence_chain.map(s => `<li>${escape(s.description)} <small>${escape(s.supporting_entity_ids.join(", "))}</small></li>`).join("")}</ol></section>
  <section><h2>Approximate image regions</h2><ul>${(report.regions?.entities ?? []).map(e => `<li><strong>${escape(e.id)} — ${escape(e.label)}</strong>: ${escape(e.description)}<br><small>Normalized box: ${escape(JSON.stringify(e.bbox))}</small></li>`).join("")}</ul></section>
  <section><h2>Review notes</h2><p>${escape(report.review?.critic_notes ?? "No additional automated review was requested.")}</p></section>
  <section><h2>Limitations</h2><ul>${(finding.limitations ?? ["Synthetic results do not evaluate the image."]).map(l=>`<li>${escape(l)}</li>`).join("")}</ul></section>
  <footer><small>Keep this record with your field observations. You can print this file or save it as PDF from your browser.</small></footer></html>`;
  const url = URL.createObjectURL(new Blob([html], {type: "text/html"}));
  const link = document.createElement("a"); link.href = url;
  link.download = `virgoeye-inspection-${report.exported_at.slice(0,10)}.html`;
  link.click(); setTimeout(() => URL.revokeObjectURL(url), 1000);
}
