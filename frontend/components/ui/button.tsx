import * as React from "react";
import { cn } from "@/lib/utils";

type Variant = "primary" | "outline" | "ghost" | "danger";
type Size = "sm" | "md" | "lg";

const variantCls: Record<Variant, string> = {
  primary: "bg-virgo-accent text-virgo-bg hover:bg-virgo-accent/90",
  outline: "border border-virgo-border text-virgo-text hover:bg-virgo-accent/10",
  ghost: "text-virgo-muted hover:text-virgo-text hover:bg-virgo-panel",
  danger: "bg-virgo-danger/10 text-virgo-danger border border-virgo-danger/40 hover:bg-virgo-danger/20",
};

const sizeCls: Record<Size, string> = {
  sm: "h-8 px-3 text-xs",
  md: "h-10 px-4 text-sm",
  lg: "h-12 px-6 text-base",
};

export interface ButtonProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: Variant;
  size?: Size;
}

export const Button = React.forwardRef<HTMLButtonElement, ButtonProps>(
  ({ className, variant = "primary", size = "md", ...props }, ref) => (
    <button
      ref={ref}
      className={cn(
        "inline-flex items-center justify-center gap-2 rounded-lg font-medium font-mono transition-colors disabled:opacity-40 disabled:pointer-events-none focus:outline-none focus-visible:ring-2 focus-visible:ring-virgo-accent/50",
        variantCls[variant],
        sizeCls[size],
        className
      )}
      {...props}
    />
  )
);
Button.displayName = "Button";