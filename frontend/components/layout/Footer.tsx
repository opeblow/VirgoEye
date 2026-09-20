import { cn } from "@/lib/utils";

interface FooterProps {
  gpuUtil?: number;
  vramUsed?: number;
  vramTotal?: number;
  className?: string;
}

export function Footer({ gpuUtil, vramUsed, vramTotal, className }: FooterProps) {
  return (
    <footer
      className={cn(
        "flex items-center justify-between px-6 py-2 border-t border-virgo-border/60 bg-virgo-panel/90 backdrop-blur-md text-[10px] font-mono text-virgo-muted",
        className
      )}
    >
      <span>Virgo-Eye v2.0 &middot; Crop inspection workspace</span>
      <div className="flex items-center gap-4">
        {vramTotal !== undefined && vramTotal > 0 && (
          <span>
            GPU {gpuUtil?.toFixed(0) ?? "0"}% &middot; VRAM{" "}
            {(vramUsed ?? 0).toFixed(0)}/{vramTotal.toFixed(0)} MB
          </span>
        )}
        <span className="text-virgo-dim">Earth Forward · Inspection support</span>
      </div>
    </footer>
  );
}
