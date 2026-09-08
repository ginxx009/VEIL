import { cn } from "@/lib/utils";

export function VeilMark({ className }: { className?: string }) {
  return (
    <svg viewBox="0 0 32 32" className={cn("size-7", className)} aria-hidden>
      <rect
        x="3.5"
        y="7.5"
        width="17"
        height="17"
        rx="4"
        fill="none"
        stroke="currentColor"
        strokeWidth="1.6"
      />
      <rect
        x="11.5"
        y="7.5"
        width="17"
        height="17"
        rx="4"
        fill="none"
        stroke="currentColor"
        strokeWidth="1.6"
        strokeDasharray="2.4 2.2"
        opacity="0.45"
      />
    </svg>
  );
}

export function VeilWordmark({ className }: { className?: string }) {
  return (
    <span className={cn("inline-flex items-center gap-2 text-foreground", className)}>
      <VeilMark className="size-6" />
      <span className="font-display text-xl tracking-tight">VEIL</span>
    </span>
  );
}
