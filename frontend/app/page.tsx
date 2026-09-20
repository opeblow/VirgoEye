import Link from "next/link";
import { ArrowUpRight, Scan, ShieldCheck, ClipboardList } from "lucide-react";
export default function LandingPage() {
  return <main className="min-h-screen bg-[#f3f6ed] text-[#173b2a]">
    <nav className="max-w-7xl mx-auto flex items-center justify-between px-6 py-6 border-b border-[#173b2a]/15">
      <Link href="/" className="font-bold tracking-tight text-xl">VirgoEye ↗</Link>
      <Link href="/dashboard" className="text-sm font-medium flex gap-2 items-center">Open workspace <ArrowUpRight size={16}/></Link>
    </nav>
    <section className="max-w-7xl mx-auto px-6 py-16 md:py-24 grid md:grid-cols-2 gap-12 items-center">
      <div>
        <p className="text-xs uppercase tracking-[0.24em] mb-6">Observe carefully. Act with evidence.</p>
        <h1 className="text-5xl md:text-7xl leading-[1.06] tracking-tight font-semibold">A clearer view.<br/><span className="text-[#648637]">A better field check.</span></h1>
        <p className="mt-7 text-lg leading-relaxed max-w-lg text-[#47614c]">Turn crop images into inspection priorities. Locate visible concerns, examine the evidence, and take a practical report into the field.</p>
        <Link href="/dashboard" className="inline-flex items-center gap-6 rounded-full bg-[#173b2a] text-white px-7 py-4 mt-8 font-medium">Start an inspection <ArrowUpRight size={20}/></Link>
        <p className="text-xs mt-4 text-[#61735c]">No account required locally · Claude image analysis when configured</p>
      </div>
      <div className="rounded-[2rem] bg-[#183f2d] p-7 md:p-10 text-white shadow-xl">
        <div className="flex justify-between text-xs uppercase tracking-widest text-[#c7d8a6]"><span>The inspection loop</span><span>01 — 04</span></div>
        <div className="mt-8">{[
          ["01", "Locate", "Approximate image regions anchor the observations."],
          ["02", "Observe", "Visible evidence is separated from possible explanations."],
          ["03", "Challenge", "An automated reviewer checks the initial findings."],
          ["04", "Follow up", "Unverified findings are marked for human review."],
        ].map(([n,title,text])=><div key={n} className="py-6 border-t border-white/15 flex gap-5"><span className="text-[#b4cc82] font-mono text-sm pt-1">{n}</span><div><h2 className="text-2xl font-medium">{title}</h2><p className="text-sm text-white/65 mt-2">{text}</p></div></div>)}</div>
        <p className="text-xs text-white/55 border-t border-white/15 pt-5">Workflow illustration · not an example analysis result</p>
      </div>
    </section>
    <section className="max-w-7xl mx-auto px-6 pb-20 grid md:grid-cols-3 gap-5">{[
      {icon: Scan,title:"Evidence you can inspect",body:"Select image regions and read the observations behind the finding. Locations are approximate, ready for your review."},
      {icon: ShieldCheck,title:"Uncertainty stays visible",body:"A rejected analysis cannot become an automated all-clear. Model estimates are not measured probabilities."},
      {icon: ClipboardList,title:"Take the next step",body:"Download an inspection record with observations, reviewer feedback and suggested field checks."},
    ].map(({icon:Icon,title,body})=><article key={title} className="rounded-2xl border border-[#173b2a]/15 p-7 bg-white/50"><Icon size={25}/><h2 className="font-semibold text-xl mt-5">{title}</h2><p className="text-sm leading-relaxed text-[#61735c] mt-3">{body}</p></article>)}</section>
    <footer className="max-w-7xl mx-auto px-6 py-7 border-t border-[#173b2a]/15 text-xs text-[#61735c] flex flex-wrap justify-between gap-3"><span>VirgoEye · Earth Forward</span><span>Visual inspection support. Confirm findings in the field.</span></footer>
  </main>;
}
