"use client";
import { useEffect, useRef, useState } from "react";
import { cn } from "@/lib/utils";

interface TypewriterTextProps {
  text: string;
  speed?: number;
  className?: string;
  onComplete?: () => void;
}

export function TypewriterText({ text, speed = 8, className, onComplete }: TypewriterTextProps) {
  const [displayed, setDisplayed] = useState("");
  const idx = useRef(0);
  const intervalRef = useRef<ReturnType<typeof setInterval>>(null);

  useEffect(() => {
    idx.current = 0;
    setDisplayed("");
    intervalRef.current = setInterval(() => {
      if (idx.current >= text.length) {
        clearInterval(intervalRef.current!);
        onComplete?.();
        return;
      }
      const chunk = text.slice(idx.current, idx.current + speed);
      idx.current += speed;
      setDisplayed((prev) => prev + chunk);
    }, 16);
    return () => {
      if (intervalRef.current) clearInterval(intervalRef.current);
    };
  }, [text, speed]);

  return (
    <span className={cn("font-mono", className)}>
      {displayed}
      {displayed.length < text.length && (
        <span className="inline-block w-[2px] h-[1em] bg-virgo-accent ml-px animate-typewriterCursor" />
      )}
    </span>
  );
}
