import { Mic, MicOff, MonitorUp, Phone, Video } from "lucide-react";
import { cn } from "@/lib/utils";
import {
  CODE_PROBLEM,
  MEETING_DOC,
  MODE_COPY,
  SALES_SLIDE,
} from "@/lib/sample-data";
import { formatClock } from "@/lib/utils";
import type { MeetingMode } from "@/lib/types";

function Tile({
  initials,
  name,
  you,
  compact,
}: {
  initials: string;
  name: string;
  you?: boolean;
  compact?: boolean;
}) {
  return (
    <div
      className={cn(
        "relative overflow-hidden rounded-md bg-secondary",
        compact ? "h-16 w-24" : "aspect-video min-h-24",
      )}
    >
      <div className="flex h-full items-center justify-center">
        <span
          className={cn(
            "flex items-center justify-center rounded-full bg-accent font-medium text-foreground",
            compact ? "size-8 text-xs" : "size-12 text-sm",
          )}
        >
          {initials}
        </span>
      </div>
      <div className="absolute inset-x-0 bottom-0 flex items-center justify-between px-2 py-1.5">
        <span className="text-xs text-foreground/90">{name}</span>
        {you ? <Mic className="size-3 text-sage" /> : <MicOff className="size-3 text-muted-foreground" />}
      </div>
    </div>
  );
}

function SharedScreen({ mode }: { mode: MeetingMode }) {
  if (mode === "sales") {
    return (
      <div className="flex h-full flex-col justify-between rounded-md bg-background p-5 shadow-[var(--shadow-border)]">
        <p className="text-xs uppercase tracking-widest text-muted-foreground">{SALES_SLIDE.kicker}</p>
        <h3 className="font-display text-2xl leading-snug text-foreground md:text-3xl">{SALES_SLIDE.title}</h3>
        <ul className="space-y-2 text-sm text-muted-foreground">
          {SALES_SLIDE.bullets.map((b) => (
            <li key={b} className="flex gap-2">
              <span className="mt-2 size-1 shrink-0 rounded-full bg-sage" />
              {b}
            </li>
          ))}
        </ul>
      </div>
    );
  }

  if (mode === "meeting") {
    return (
      <div className="h-full rounded-md bg-background p-5 shadow-[var(--shadow-border)]">
        <p className="text-xs uppercase tracking-widest text-muted-foreground">Shared doc</p>
        <h3 className="mt-2 font-display text-xl text-foreground">{MEETING_DOC.title}</h3>
        <ul className="mt-4 space-y-2.5 text-sm text-muted-foreground">
          {MEETING_DOC.lines.map((line) => (
            <li key={line} className="rounded-sm bg-secondary px-3 py-2 text-foreground/90">
              {line}
            </li>
          ))}
        </ul>
      </div>
    );
  }

  return (
    <div className="flex h-full flex-col overflow-hidden rounded-md bg-background shadow-[var(--shadow-border)]">
      <div className="flex items-center justify-between border-b border-border px-3 py-2">
        <span className="text-xs text-muted-foreground">{CODE_PROBLEM.title}</span>
        <span className="font-mono text-xs text-muted-foreground">pad · typescript</span>
      </div>
      <div className="min-h-0 flex-1 overflow-auto p-3 font-mono text-xs leading-relaxed">
        <p className="text-muted-foreground">{CODE_PROBLEM.prompt}</p>
        <pre className="mt-3 whitespace-pre-wrap text-foreground/90">{CODE_PROBLEM.signature}</pre>
        <p className="mt-3 text-sage">{CODE_PROBLEM.tests}</p>
      </div>
    </div>
  );
}

export function screenContentText(mode: MeetingMode) {
  if (mode === "sales") {
    return `${SALES_SLIDE.kicker}\n${SALES_SLIDE.title}\n${SALES_SLIDE.bullets.join("\n")}`;
  }
  if (mode === "meeting") {
    return `${MEETING_DOC.title}\n${MEETING_DOC.lines.join("\n")}`;
  }
  return `${CODE_PROBLEM.title}\n${CODE_PROBLEM.prompt}\n${CODE_PROBLEM.signature}\n${CODE_PROBLEM.tests}`;
}

export function MeetingStage({
  mode,
  youName,
  elapsed,
  className,
}: {
  mode: MeetingMode;
  youName: string;
  elapsed: number;
  compact?: boolean;
  className?: string;
}) {
  const copy = MODE_COPY[mode];
  const youInitials = youName
    .split(" ")
    .map((p) => p[0])
    .join("")
    .slice(0, 2)
    .toUpperCase();
  const themInitials = copy.interviewer
    .split(" ")
    .map((p) => p[0])
    .join("")
    .slice(0, 2)
    .toUpperCase();

  return (
    <div className={cn("flex h-full min-h-0 flex-col bg-background text-foreground", className)}>
      <div className="flex items-center justify-between px-3 py-2 text-xs text-muted-foreground">
        <span className="truncate">{copy.meeting}</span>
        <span className="tabular-nums">{formatClock(elapsed)}</span>
      </div>
      <div className="grid min-h-0 flex-1 grid-cols-1 gap-2 px-2 sm:grid-cols-[1fr_auto]">
        <SharedScreen mode={mode} />
        <div className="flex w-auto flex-row gap-2 sm:w-28 sm:flex-col">
          <Tile initials={themInitials} name={copy.interviewer} compact />
          <Tile initials={youInitials || "YO"} name={youName.split(" ")[0] || "You"} you compact />
        </div>
      </div>
      <div className="flex items-center justify-center gap-2 py-3">
        <span className="flex size-9 items-center justify-center rounded-full bg-secondary text-foreground">
          <Mic className="size-4" />
        </span>
        <span className="flex size-9 items-center justify-center rounded-full bg-secondary text-foreground">
          <Video className="size-4" />
        </span>
        <span className="flex size-9 items-center justify-center rounded-full bg-sage-dim text-sage">
          <MonitorUp className="size-4" />
        </span>
        <span className="flex size-9 items-center justify-center rounded-full bg-destructive text-destructive-foreground">
          <Phone className="size-4 rotate-hang" />
        </span>
      </div>
    </div>
  );
}
