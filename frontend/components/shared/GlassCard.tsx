import { cn } from "@/lib/utils";

interface GlassCardProps {
  children: React.ReactNode;
  className?: string;
  noPad?: boolean;
}

export function GlassCard({ children, className, noPad }: GlassCardProps) {
  return (
    <div
      className={cn(
        "rounded-2xl border border-virgo-border/60 bg-virgo-panel/80 backdrop-blur-md shadow-[0_0_24px_rgba(22,163,74,0.05)]",
        !noPad && "p-5",
        className
      )}
    >
      {children}
    </div>
  );
}
