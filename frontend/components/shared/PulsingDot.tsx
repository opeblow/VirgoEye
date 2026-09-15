import { cn } from "@/lib/utils";

interface PulsingDotProps {
  color?: "green" | "amber" | "red" | "blue";
  className?: string;
  size?: "sm" | "md" | "lg";
}

const colorMap = {
  green: "bg-virgo-ok",
  amber: "bg-virgo-warn",
  red: "bg-virgo-danger",
  blue: "bg-virgo-accent",
};

const sizeMap = {
  sm: "w-2 h-2",
  md: "w-3 h-3",
  lg: "w-4 h-4",
};

export function PulsingDot({ color = "green", className, size = "md" }: PulsingDotProps) {
  return (
    <span className={cn("relative inline-flex h-3 w-3", className)}>
      <span
        className={cn(
          "absolute inline-flex h-full w-full animate-ping rounded-full opacity-60",
          colorMap[color]
        )}
      />
      <span className={cn("relative inline-flex rounded-full", sizeMap[size], colorMap[color])} />
    </span>
  );
}
