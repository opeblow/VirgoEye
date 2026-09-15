import Link from "next/link";
import {
  Boxes,
  Brain,
  Gauge,
  GitCompareArrows,
  ListChecks,
  Microscope,
  Radar,
  Rocket,
  ShieldCheck,
  Sparkles,
  Workflow,
} from "lucide-react";

const STAGES = [
  {
    n: "01",
    icon: Radar,
    title: "Spatial Mapping",
    desc: "Every entity is located, labelled, and boxed with a confidence before we reason about anything.",
  },
  {
    n: "02",
    icon: Brain,
    title: "CoVT Deliberation",
    desc: "An explicit <thought> chain reasons spatially, then relationally, then causally — streamed live.",
  },
  {
    n: "03",
    icon: ShieldCheck,
    title: "Critic Verification",
    desc: "A counter-factual pass hunts hallucinations, logical fallacies, and entities the model missed.",
  },
  {
    n: "04",
    icon: Rocket,
    title: "Calibrated Verdict",
    desc: "Severity, confidence, and an evidence chain that only survives if the critic couldn't break it.",
  },
];

const FEATURES = [
  {
    icon: Workflow,
    title: "Self-verifying pipeline",
    desc: "Each stage is gated by strict typed contracts. A broken map can't silently poison the verdict.",
  },
  {
    icon: Gauge,
    title: "Streaming, not blocking",
    desc: "SSE frames surface every stage as it happens — perceived latency is first-token, not completion.",
  },
  {
    icon: Microscope,
    title: "4-bit AWQ quantization",
    desc: "A 7B vision model runs in ~4 GB of VRAM with KV-cache bookkeeping across all four stages.",
  },
  {
    icon: GitCompareArrows,
    title: "No-GPU demo mode",
    desc: "An image-aware demo engine keeps the entire pipeline demonstrable anywhere, anytime.",
  },
];

const DOMAINS = ["PCB & electronics", "Medical imaging", "Architecture plans", "Satellite / aerial"];

export default function LandingPage() {
  return (
    <div className="min-h-screen flex flex-col bg-virgo-bg">
      {/* Top nav */}
      <nav className="flex items-center justify-between px-6 md:px-10 py-4 border-b border-virgo-border/60 bg-virgo-panel/70 backdrop-blur-md sticky top-0 z-20">
        <Link href="/" className="flex items-center gap-3">
          <div className="w-9 h-9 rounded-xl bg-gradient-to-br from-virgo-accent to-virgo-accent2 flex items-center justify-center">
            <span className="text-white font-bold text-sm">VE</span>
          </div>
          <span className="text-lg font-semibold tracking-tight text-virgo-text">
            VIRGO<span className="text-virgo-accent">-EYE</span>
          </span>
        </Link>
        <Link
          href="/dashboard"
          className="inline-flex items-center gap-2 h-10 px-5 rounded-lg bg-virgo-accent text-white font-medium font-mono text-sm hover:bg-virgo-accent/90 transition-colors"
        >
          <Sparkles className="w-4 h-4" />
          Launch Console
        </Link>
      </nav>

      {/* Hero */}
      <section className="relative px-6 md:px-10 pt-20 pb-16 text-center overflow-hidden">
        <div className="absolute inset-0 pointer-events-none bg-[radial-gradient(60%_50%_at_50%_0%,rgba(22,163,74,0.10),transparent)]" />
        <div className="relative max-w-3xl mx-auto">
          <span className="inline-flex items-center gap-2 px-3 py-1 rounded-full border border-virgo-accent/30 bg-virgo-accent/10 text-virgo-accent text-xs font-mono uppercase tracking-wider">
            <span className="w-1.5 h-1.5 rounded-full bg-virgo-accent animate-pulse" />
            Chain-of-Visual-Thought Engine
          </span>

          <h1 className="mt-6 text-4xl md:text-6xl font-black tracking-tight text-virgo-text leading-[1.05]">
            Fast models glance.
            <br />
            <span className="text-virgo-accent">Virgo-Eye deliberates.</span>
          </h1>

          <p className="mt-6 text-lg text-virgo-muted leading-relaxed max-w-2xl mx-auto">
            A reasoning-first multimodal diagnostic engine that forces a
            vision-language model to <strong className="text-virgo-text">map every entity</strong>,
            <strong className="text-virgo-text"> reason over relationships</strong>,{" "}
            <strong className="text-virgo-text">verify against itself</strong>, and only then emit a
            calibrated verdict — streamed live to a real-time dashboard.
          </p>

          <div className="mt-10 flex flex-col sm:flex-row items-center justify-center gap-4">
            <Link
              href="/dashboard"
              className="inline-flex items-center gap-2 h-13 px-8 py-4 rounded-xl bg-gradient-to-br from-virgo-accent to-emerald-600 text-white font-semibold font-mono text-base shadow-lg shadow-virgo-accent/25 hover:shadow-virgo-accent/40 hover:-translate-y-0.5 transition-all"
            >
              <Boxes className="w-5 h-5" />
              Run a Diagnostic
            </Link>
            <a
              href="#pipeline"
              className="inline-flex items-center gap-2 h-13 px-8 py-4 rounded-xl border border-virgo-border bg-white text-virgo-text font-medium font-mono text-base hover:border-virgo-accent/50 hover:text-virgo-accent transition-colors"
            >
              How it works
            </a>
          </div>

          <p className="mt-6 text-xs font-mono text-virgo-dim">
            Works in demo mode with zero GPU &middot; drop in Qwen2-VL-7B for real inference
          </p>
        </div>
      </section>

      {/* Pipeline */}
      <section id="pipeline" className="px-6 md:px-10 py-16 scroll-mt-20">
        <div className="max-w-6xl mx-auto">
          <div className="text-center mb-12">
            <h2 className="text-3xl font-bold text-virgo-text">Four stages. Zero shortcuts.</h2>
            <p className="mt-3 text-virgo-muted">
              The 4-stage CoVT pipeline — each stage independently observable and hard-gated.
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
            {STAGES.map((s, i) => (
              <div key={s.n} className="group relative">
                <div className="h-full rounded-2xl border border-virgo-border bg-white p-6 flex flex-col gap-4 hover:border-virgo-accent/40 hover:shadow-lg hover:shadow-virgo-accent/10 transition-shadow">
                  <div className="flex items-center justify-between">
                    <span className="w-11 h-11 rounded-xl bg-virgo-accent/10 flex items-center justify-center">
                      <s.icon className="w-5 h-5 text-virgo-accent" />
                    </span>
                    <span className="text-2xl font-black font-mono text-virgo-border">{s.n}</span>
                  </div>
                  <h3 className="font-semibold text-virgo-text">{s.title}</h3>
                  <p className="text-sm text-virgo-muted leading-relaxed">{s.desc}</p>
                </div>
                {i < STAGES.length - 1 && (
                  <div className="hidden md:flex absolute top-1/2 -right-4 w-8 items-center justify-center text-virgo-accent">
                    <Workflow className="w-5 h-5" />
                  </div>
                )}
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Features + domains */}
      <section className="px-6 md:px-10 py-16 bg-white border-y border-virgo-border/60">
        <div className="max-w-6xl mx-auto grid grid-cols-1 lg:grid-cols-2 gap-10">
          <div>
            <h2 className="text-2xl font-bold text-virgo-text mb-6">Engineered for speed & trust</h2>
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
              {FEATURES.map((f) => (
                <div key={f.title} className="rounded-2xl border border-virgo-border bg-virgo-bg p-5">
                  <f.icon className="w-5 h-5 text-virgo-accent mb-3" />
                  <h3 className="text-sm font-semibold text-virgo-text mb-1">{f.title}</h3>
                  <p className="text-xs text-virgo-muted leading-relaxed">{f.desc}</p>
                </div>
              ))}
            </div>
          </div>

          <div>
            <h2 className="text-2xl font-bold text-virgo-text mb-6">
              Built for fields where one glance isn&apos;t enough
            </h2>
            <div className="space-y-3">
              {DOMAINS.map((d) => (
                <div
                  key={d}
                  className="flex items-center gap-3 rounded-2xl border border-virgo-border bg-white px-5 py-4 hover:border-virgo-accent/40 transition-colors"
                >
                  <ListChecks className="w-4 h-4 text-virgo-accent shrink-0" />
                  <span className="font-mono text-sm text-virgo-text">{d}</span>
                </div>
              ))}
            </div>
            <p className="mt-5 text-sm text-virgo-muted leading-relaxed">
              Upload any image, pick a domain, and the pipeline will map, reason,
              verify and report — degree-of-confidence and all.
            </p>
          </div>
        </div>
      </section>

      {/* CTA */}
      <section className="px-6 md:px-10 py-20">
        <div className="max-w-4xl mx-auto rounded-3xl bg-gradient-to-br from-virgo-accent to-emerald-700 text-white text-center px-8 py-14 shadow-xl shadow-virgo-accent/25">
          <h2 className="text-3xl md:text-4xl font-black tracking-tight">
            Watch it think.
          </h2>
          <p className="mt-4 text-emerald-50/90 max-w-xl mx-auto">
            See every bounding box, every thought token, every critic correction
            surface in real time — no install, no GPU required.
          </p>
          <Link
            href="/dashboard"
            className="mt-8 inline-flex items-center gap-2 h-12 px-8 rounded-xl bg-white text-virgo-accent font-semibold font-mono hover:bg-emerald-50 transition-colors"
          >
            <Rocket className="w-5 h-5" />
            Go to the Console
          </Link>
        </div>
      </section>

      {/* Footer */}
      <footer className="px-6 md:px-10 py-6 border-t border-virgo-border/60 bg-white">
        <div className="max-w-6xl mx-auto flex flex-col sm:flex-row items-center justify-between gap-3 text-xs font-mono text-virgo-muted">
          <span>Virgo-Eye &middot; Chain-of-Visual-Thought Diagnostic Engine v2.0</span>
          <div className="flex items-center gap-4">
            <Link href="/dashboard" className="text-virgo-accent hover:underline">
              Console
            </Link>
            <span className="text-virgo-dim">SPEED Virgo Challenge</span>
          </div>
        </div>
      </footer>
    </div>
  );
}