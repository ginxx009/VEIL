import type { ReactNode } from "react";
import { cn } from "@/lib/utils";
import type { ViewMode } from "@/lib/types";

export function DualView({
  view,
  stealthOn,
  overlayVisible,
  you,
  them,
  overlay,
}: {
  view: ViewMode;
  stealthOn: boolean;
  overlayVisible: boolean;
  you: ReactNode;
  them: ReactNode;
  overlay: ReactNode;
}) {
  const showThemOverlay = overlayVisible && !stealthOn;
  const split = view === "split";
  const showYou = view !== "them";
  const showThem = view !== "you";

  return (
    <div
      className={cn(
        "grid min-h-0 flex-1 gap-3",
        split ? "lg:grid-cols-2" : "grid-cols-1",
      )}
    >
      {showYou ? (
        <ScreenFrame
          kicker="Your display"
          caption={overlayVisible ? "VEIL is on this machine only" : "Overlay hidden"}
          tone="you"
        >
          {you}
          {overlayVisible ? overlay : null}
        </ScreenFrame>
      ) : null}
      {showThem ? (
        <ScreenFrame
          kicker="Their screen share"
          caption={
            stealthOn
              ? "Capture compositor skipped the overlay"
              : overlayVisible
                ? "Stealth off — they can see VEIL"
                : "Overlay hidden"
          }
          tone={stealthOn || !overlayVisible ? "clean" : "exposed"}
        >
          {them}
          {showThemOverlay ? <div className="pointer-events-none opacity-90">{overlay}</div> : null}
        </ScreenFrame>
      ) : null}
    </div>
  );
}

function ScreenFrame({
  kicker,
  caption,
  tone,
  children,
}: {
  kicker: string;
  caption: string;
  tone: "you" | "clean" | "exposed";
  children: ReactNode;
}) {
  return (
    <section className="flex min-h-0 flex-col">
      <div className="mb-2 flex items-end justify-between gap-3 px-1">
        <div>
          <p className="text-[0.65rem] font-medium uppercase tracking-[0.2em] text-muted-foreground">{kicker}</p>
          <p
            className={cn(
              "text-xs",
              tone === "exposed" ? "text-warn" : tone === "clean" ? "text-sage" : "text-muted-foreground",
            )}
          >
            {caption}
          </p>
        </div>
      </div>
      <div className="relative min-h-64 flex-1 overflow-hidden rounded-xl bg-card shadow-[var(--shadow-border)]">
        <div className="pointer-events-none absolute inset-x-0 top-0 z-10 flex justify-center">
          <div className="h-4 w-24 rounded-b-md bg-secondary" />
        </div>
        <div className="absolute inset-0 pt-3">{children}</div>
      </div>
    </section>
  );
}
