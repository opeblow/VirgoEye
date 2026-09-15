"use client";
import { useCallback, useRef, useState } from "react";
import { GlassCard } from "@/components/shared/GlassCard";
import { cn } from "@/lib/utils";

interface ImageUploaderProps {
  onImageReady: (base64: string) => void;
  onClear: () => void;
  imagePreviewUrl: string | null;
  disabled?: boolean;
}

export function ImageUploader({
  onImageReady,
  onClear,
  imagePreviewUrl,
  disabled,
}: ImageUploaderProps) {
  const [dragOver, setDragOver] = useState(false);
  const [localPreview, setLocalPreview] = useState<string | null>(null);
  const inputRef = useRef<HTMLInputElement>(null);

  const show = imagePreviewUrl ?? localPreview;

  const handleFile = useCallback(
    (file: File) => {
      if (!file.type.startsWith("image/")) return;
      const reader = new FileReader();
      reader.onload = () => {
        const dataUrl = String(reader.result ?? "");
        const b64 = dataUrl.split(",")[1] ?? "";
        setLocalPreview(dataUrl);
        onImageReady(b64);
      };
      reader.readAsDataURL(file);
    },
    [onImageReady]
  );

  const handleClear = () => {
    setLocalPreview(null);
    onClear();
  };

  return (
    <GlassCard className="flex flex-col gap-4" noPad>
      <label
        className={cn(
          "relative flex flex-col items-center justify-center gap-3 rounded-2xl border-2 border-dashed min-h-[260px] p-6 transition-colors cursor-pointer",
          dragOver
            ? "border-virgo-accent bg-virgo-accent/5"
            : "border-virgo-border",
          disabled && "opacity-50 pointer-events-none"
        )}
        onDragOver={(e) => {
          e.preventDefault();
          setDragOver(true);
        }}
        onDragLeave={() => setDragOver(false)}
        onDrop={(e) => {
          e.preventDefault();
          setDragOver(false);
          const f = e.dataTransfer.files?.[0];
          if (f) handleFile(f);
        }}
      >
        {show ? (
          <img
            src={show}
            alt="Uploaded diagnostic image"
            className="max-h-72 rounded-lg object-contain"
          />
        ) : (
          <>
            <div className="w-14 h-14 rounded-xl bg-virgo-accent/10 flex items-center justify-center">
              <svg
                className="w-7 h-7 text-virgo-accent"
                fill="none"
                viewBox="0 0 24 24"
                stroke="currentColor"
                strokeWidth={1.5}
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  d="M2.25 15.75l5.159-5.159a2.25 2.25 0 013.182 0l5.159 5.159m-1.5-1.5l1.409-1.409a2.25 2.25 0 013.182 0l2.909 2.909m-18 3.75h16.5a1.5 1.5 0 001.5-1.5V6a1.5 1.5 0 00-1.5-1.5H3.75A1.5 1.5 0 002.25 6v12a1.5 1.5 0 001.5 1.5zm10.5-11.25h.008v.008h-.008V8.25zm.375 0a.375.375 0 11-.75 0 .375.375 0 01.75 0z"
                />
              </svg>
            </div>
            <div className="text-center">
              <p className="text-virgo-text font-medium">
                Drag &amp; drop an image, paste, or click to browse
              </p>
              <p className="text-xs text-virgo-muted mt-1">
                PCB / medical / architecture / satellite
              </p>
            </div>
          </>
        )}
        <input
          ref={inputRef}
          type="file"
          accept="image/*"
          className="sr-only"
          onChange={(e) => {
            const f = e.target.files?.[0];
            if (f) handleFile(f);
            e.currentTarget.value = "";
          }}
        />
      </label>
      {show && (
        <button
          className="text-xs font-mono text-virgo-danger hover:underline self-end"
          onClick={(e) => {
            e.preventDefault();
            e.stopPropagation();
            handleClear();
          }}
        >
          [x] clear image
        </button>
      )}
    </GlassCard>
  );
}