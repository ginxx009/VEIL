import type { ReactNode } from "react";
import { Copy, Eye, EyeOff, Keyboard, Monitor, CornerDownLeft, X } from "lucide-react";
import { toast } from "sonner";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { cn, modKeyLabel } from "@/lib/utils";
import type { AssistResult, AssistStatus } from "@/lib/types";

export function OverlayPanel({
  stealthOn,
  visible,
  status,
  result,
  error,
  prompt,
  onPrompt,
  onAssist,
  onScreen,
  onToggleStealth,
  onHide,
  compact,
}: {
  stealthOn: boolean;
  visible: boolean;
  status: AssistStatus;
  result: AssistResult | null;
  error: string | null;
  prompt: string;
  onPrompt: (v: string) => void;
  onAssist: () => void;
  onScreen: () => void;
  onToggleStealth: () => void;
  onHide: () => void;
  compact?: boolean;
}) {
  if (!visible) return null;
  const mod = modKeyLabel();

  return (
    <div
      className={cn(
        "pointer-events-auto absolute inset-x-3 top-3 z-20 flex max-h-[calc(100%-0.75rem)] flex-col gap-2 overflow-y-auto",
        compact ? "max-w-full" : "mx-auto max-w-lg",
      )}
    >
      <div className="flex items-center gap-1 rounded-full bg-card/92 px-1.5 py-1 shadow-[var(--shadow-border),var(--shadow-float)] backdrop-blur-md">
        <Badge variant={stealthOn ? "sage" : "warn"} className="ml-1 shrink-0">
          {stealthOn ? "Stealth on" : "Visible"}
        </Badge>
        <button
          type="button"
          onClick={onAssist}
          className="rounded-full px-3 py-1.5 text-xs font-medium text-foreground hover:bg-accent"
        >
          Assist
        </button>
        <button
          type="button"
          onClick={onScreen}
          className="hidden rounded-full px-3 py-1.5 text-xs font-medium text-muted-foreground hover:bg-accent hover:text-foreground sm:inline"
        >
          Screen
        </button>
        <div className="ml-auto flex items-center">
          <IconBtn
            label={stealthOn ? "Show on share" : "Hide from share"}
            onClick={onToggleStealth}
          >
            {stealthOn ? <EyeOff className="size-3.5" /> : <Eye className="size-3.5" />}
          </IconBtn>
          <IconBtn label="Hide overlay" onClick={onHide}>
            <X className="size-3.5" />
          </IconBtn>
        </div>
      </div>

      <form
        className="flex gap-2 rounded-xl bg-card/92 p-2 shadow-[var(--shadow-border)] backdrop-blur-md"
        onSubmit={(e) => {
          e.preventDefault();
          onAssist();
        }}
      >
        <Input
          value={prompt}
          onChange={(e) => onPrompt(e.target.value)}
          placeholder={`Ask, or ${mod}+Enter for Assist`}
          className="h-10 rounded-lg bg-transparent shadow-none focus-visible:ring-0"
        />
        <Button type="submit" size="sm" className="h-10 rounded-lg px-3">
          <CornerDownLeft className="size-3.5" />
          Go
        </Button>
      </form>

      <div className="rounded-xl bg-card/92 p-3.5 shadow-[var(--shadow-border)] backdrop-blur-md">
        {status === "thinking" ? (
          <p className="veil-shimmer bg-clip-text text-sm text-muted-foreground">Writing a speakable answer…</p>
        ) : status === "error" ? (
          <p className="text-sm text-destructive">{error ?? "Could not generate an answer."}</p>
        ) : result ? (
          <div className="space-y-3">
            <div className="flex items-center justify-between gap-2">
              <p className="text-xs font-medium uppercase tracking-widest text-muted-foreground">Answer</p>
              <Button
                type="button"
                variant="ghost"
                size="icon-sm"
                className="size-8 shrink-0"
                onClick={() => {
                  void navigator.clipboard.writeText(
                    [result.spoken, result.points.map((p) => `• ${p}`).join("\n"), result.code]
                      .filter(Boolean)
                      .join("\n\n"),
                  );
                  toast.success("Copied");
                }}
              >
                <Copy className="size-3.5" />
              </Button>
            </div>
            <p className="text-sm leading-relaxed text-foreground">{result.spoken}</p>
            {result.points.length > 0 ? (
              <ul className="space-y-1">
                {result.points.map((p) => (
                  <li key={p} className="flex gap-2 text-xs text-muted-foreground">
                    <span className="mt-1 size-1 shrink-0 rounded-full bg-sage" />
                    {p}
                  </li>
                ))}
              </ul>
            ) : null}
            {result.code ? (
              <pre className="overflow-x-auto rounded-md bg-background p-2.5 font-mono text-xs leading-relaxed text-sage">
                {result.code}
              </pre>
            ) : null}
          </div>
        ) : (
          <div className="space-y-2 text-xs text-muted-foreground">
            <p className="flex items-center gap-2">
              <Keyboard className="size-3.5" />
              {mod}+Enter assist · {mod}+Shift+E stealth · {mod}+Shift+H hide
            </p>
            <p className="flex items-center gap-2">
              <Monitor className="size-3.5" />
              {stealthOn
                ? "Excluded from the shared frame. Their share stays clean."
                : "Stealth is off — the overlay will appear on their screen share."}
            </p>
          </div>
        )}
      </div>
    </div>
  );
}

function IconBtn({
  children,
  label,
  onClick,
}: {
  children: ReactNode;
  label: string;
  onClick: () => void;
}) {
  return (
    <button
      type="button"
      aria-label={label}
      title={label}
      onClick={onClick}
      className="flex size-9 items-center justify-center rounded-full text-muted-foreground hover:bg-accent hover:text-foreground"
    >
      {children}
    </button>
  );
}
