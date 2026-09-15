import { cn } from "@/lib/utils";

type BadgeTone = "default" | "accent" | "success" | "warning" | "danger" | "purple";

const toneCls: Record<BadgeTone, string> = {
  default: "bg-virgo-border/60 text-virgo-muted",
  accent: "bg-virgo-accent/15 text-virgo-accent",
  success: "bg-virgo-ok/15 text-virgo-ok",
  warning: "bg-virgo-warn/15 text-virgo-warn",
  danger: "bg-virgo-danger/15 text-virgo-danger",
  purple: "bg-virgo-accent2/15 text-virgo-accent2",
};

export function Badge({
  tone = "default",
  className,
  children,
}: {
  tone?: BadgeTone;
  className?: string;
  children: React.ReactNode;
}) {
  return (
    <span
      className={cn(
        "inline-flex items-center gap-1 px-2 py-0.5 rounded-md text-[10px] font-mono uppercase tracking-wider",
        toneCls[tone],
        className
      )}
    >
      {children}
    </span>
  );
}